-- 한줄 Supabase schema
-- Run in Supabase SQL editor after creating a project.

create extension if not exists "pgcrypto";

-- ---------------------------------------------------------------------------
-- Profiles (anonymous by design: no real name, phone, address, photo)
-- ---------------------------------------------------------------------------
create table if not exists public.profiles (
  id          uuid primary key references auth.users (id) on delete cascade,
  nickname    text not null,
  grade       int  not null check (grade between 1 and 3),
  class_no    text not null,
  track       text,
  region      text not null default '경기도 광명시',
  created_at  timestamptz not null default now()
);

-- ---------------------------------------------------------------------------
-- Private learning logs
-- ---------------------------------------------------------------------------
create table if not exists public.logs (
  id          uuid primary key default gen_random_uuid(),
  user_id     uuid not null references public.profiles (id) on delete cascade,
  date        date not null,
  period      int  not null,
  subject     text not null,
  learned     text not null check (char_length(learned) <= 120),
  activity    text,
  stuck       text,
  is_public   boolean not null default false,
  created_at  timestamptz not null default now(),
  unique (user_id, date, period)
);

-- ---------------------------------------------------------------------------
-- Public, sanitized post copy
-- ---------------------------------------------------------------------------
create table if not exists public.posts (
  id          uuid primary key default gen_random_uuid(),
  log_id      uuid unique references public.logs (id) on delete cascade,
  user_id     uuid not null references public.profiles (id) on delete cascade,
  nickname    text not null,
  grade       int  not null,
  subject     text,
  public_text text not null,
  concept_tags text[] not null default '{}',
  region      text not null default '경기도 광명시',
  status      text not null default 'visible' check (status in ('visible', 'hidden', 'deleted')),
  reports     int not null default 0,
  created_at  timestamptz not null default now()
);

create table if not exists public.reactions (
  id         uuid primary key default gen_random_uuid(),
  post_id    uuid not null references public.posts (id) on delete cascade,
  user_id    uuid not null references public.profiles (id) on delete cascade,
  type       text not null default 'cheer',
  created_at timestamptz not null default now(),
  unique (post_id, user_id)
);

create table if not exists public.reports (
  id          uuid primary key default gen_random_uuid(),
  post_id     uuid not null references public.posts (id) on delete cascade,
  reporter_id uuid not null references public.profiles (id) on delete cascade,
  reason      text,
  status      text not null default 'open',
  created_at  timestamptz not null default now()
);

-- ---------------------------------------------------------------------------
-- Spaced repetition
-- ---------------------------------------------------------------------------
create table if not exists public.recall_queue (
  id            uuid primary key default gen_random_uuid(),
  user_id       uuid not null references public.profiles (id) on delete cascade,
  concept       text not null,
  due_date      date not null,
  interval_days int not null default 1,
  ease          numeric(4, 2) not null default 2.5,
  reps          int not null default 0,
  last_reviewed timestamptz,
  unique (user_id, concept)
);

-- ---------------------------------------------------------------------------
-- Indexes
-- ---------------------------------------------------------------------------
create index if not exists idx_logs_user_date on public.logs (user_id, date);
create index if not exists idx_posts_region_created on public.posts (region, created_at desc);
create index if not exists idx_posts_status on public.posts (status);
create index if not exists idx_recall_due on public.recall_queue (user_id, due_date);

-- ---------------------------------------------------------------------------
-- Profile bootstrap
-- ---------------------------------------------------------------------------
create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer set search_path = public
as $$
begin
  insert into public.profiles (id, nickname, grade, class_no, track, region)
  values (
    new.id,
    coalesce(new.raw_user_meta_data ->> 'nickname', '고2_기록러_' || substr(new.id::text, 1, 4)),
    coalesce((new.raw_user_meta_data ->> 'grade')::int, 2),
    coalesce(new.raw_user_meta_data ->> 'class_no', '5'),
    new.raw_user_meta_data ->> 'track',
    '경기도 광명시'
  )
  on conflict (id) do nothing;
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();

-- ---------------------------------------------------------------------------
-- Row Level Security
-- ---------------------------------------------------------------------------
alter table public.profiles enable row level security;
alter table public.logs enable row level security;
alter table public.posts enable row level security;
alter table public.reactions enable row level security;
alter table public.reports enable row level security;
alter table public.recall_queue enable row level security;

create policy "profiles_select_own" on public.profiles
  for select using (auth.uid() = id);
create policy "profiles_update_own" on public.profiles
  for update using (auth.uid() = id);

create policy "logs_own_all" on public.logs
  for all using (auth.uid() = user_id) with check (auth.uid() = user_id);

create policy "posts_visible_read" on public.posts
  for select using (status = 'visible');
create policy "posts_insert_own" on public.posts
  for insert with check (auth.uid() = user_id);
create policy "posts_update_own" on public.posts
  for update using (auth.uid() = user_id);
create policy "posts_delete_own" on public.posts
  for delete using (auth.uid() = user_id);

create policy "reactions_read" on public.reactions for select using (true);
create policy "reactions_insert_own" on public.reactions
  for insert with check (auth.uid() = user_id);
create policy "reactions_delete_own" on public.reactions
  for delete using (auth.uid() = user_id);

create policy "reports_insert_own" on public.reports
  for insert with check (auth.uid() = reporter_id);
create policy "reports_select_own" on public.reports
  for select using (auth.uid() = reporter_id);

create policy "recall_own_all" on public.recall_queue
  for all using (auth.uid() = user_id) with check (auth.uid() = user_id);


-- ---------------------------------------------------------------------------
-- Report RPC: insert a report and hide after 3 reports atomically.
-- ---------------------------------------------------------------------------
create or replace function public.report_post(p_post_id uuid)
returns void
language plpgsql
security definer set search_path = public
as $$
begin
  insert into public.reports (post_id, reporter_id, reason)
  values (p_post_id, auth.uid(), '신고');

  update public.posts
  set reports = reports + 1,
      status = case when reports + 1 >= 3 then 'hidden' else status end
  where id = p_post_id;
end;
$$;

grant execute on function public.report_post(uuid) to authenticated;

-- Allow first-login profile bootstrap from the client as well as the trigger.
create policy "profiles_insert_own" on public.profiles
  for insert with check (auth.uid() = id);
