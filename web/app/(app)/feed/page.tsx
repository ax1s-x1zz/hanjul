"use client";

import { useMemo, useState } from "react";

import { Empty, Chip } from "@/components/ui";
import { HeartIcon } from "@/components/icons";
import { useDemo } from "@/lib/demo-store";
import { subjectShort, timeAgo, userInitial } from "@/lib/utils";

export default function FeedPage() {
  const { state, mode, toggleCheer, reportPost } = useDemo();
  const [subject, setSubject] = useState("전체");

  const visible = state.posts.filter((post) => !post.hidden);
  const subjects = useMemo(
    () => ["전체", ...Array.from(new Set(visible.map((post) => post.subject)))],
    [visible],
  );
  const posts = visible
    .filter((post) => subject === "전체" || post.subject === subject)
    .sort((a, b) => b.createdAt.localeCompare(a.createdAt));

  return (
    <div className="page">
      <p className="helper">
        {mode === "demo" ? "데모 피드 · " : ""}
        공개한 한 줄만 보입니다. 학교명·실명은 표시되지 않습니다.
      </p>

      <div className="chips">
        {subjects.map((item) => (
          <Chip
            key={item}
            active={subject === item}
            onClick={() => setSubject(item)}
          >
            {item === "전체" ? "전체" : subjectShort(item)}
          </Chip>
        ))}
      </div>

      {posts.length === 0 ? (
        <Empty>
          아직 공개 글이 없습니다.
          <br />
          오늘 첫 배움을 남겨보세요.
        </Empty>
      ) : (
        posts.map((post) => {
          const active = post.cheers.includes(state.user.id);
          return (
            <article className="feed-post" key={post.id}>
              <div className="feed-head">
                <span className="avatar-sm">{userInitial(post.nickname)}</span>
                <div className="feed-meta">
                  <span className="feed-name">{post.nickname}</span>
                  <span className="feed-sub">
                    고{post.grade} · {post.subject} · 익명
                  </span>
                </div>
                <span className="feed-time">{timeAgo(post.createdAt)}</span>
              </div>

              <p className="post-text">{post.text}</p>

              <div>
                {post.tags.map((tag) => (
                  <span className="tag" key={tag}>
                    {tag}
                  </span>
                ))}
              </div>

              <div className="actions">
                <button
                  type="button"
                  className={active ? "heart-btn active" : "heart-btn"}
                  onClick={() => void toggleCheer(post.id)}
                  aria-pressed={active}
                >
                  <HeartIcon fill={active ? "currentColor" : "none"} />
                  응원 {post.cheers.length}
                </button>
                <button
                  type="button"
                  className="more-btn"
                  onClick={() => void reportPost(post.id)}
                  aria-label="신고"
                >
                  ···
                </button>
              </div>
            </article>
          );
        })
      )}
    </div>
  );
}
