import "./PostItem.css";

function PostItem({ post }) {
  // Basic date formatting
  const formatDate = (timestamp) => {
    const date = new Date(timestamp);
    return date.toLocaleDateString("en-US", {
      month: "long",
      day: "numeric",
      year: "numeric",
    });
  };

  return (
    <div className="post-item">
      <div className="post-header">
        <span className="post-author">{post.authorUsername}</span>
      </div>
      <div className="post-image">
        <img src={post.imageUrl} alt={post.caption} />
      </div>
      <div className="post-actions">
        {/* Like, Comment, Share icons/buttons will go here */}
        <button className="action-button">Like</button>
        <button className="action-button">Comment</button>
      </div>
      <div className="post-likes">
        {/* Placeholder for likes count */}
        <span>{post.likesCount} likes</span>
      </div>
      <div className="post-caption">
        <span className="post-author">{post.authorUsername}</span>{" "}
        {post.caption}
      </div>
      <div className="post-comments-preview">
        {/* Placeholder for comments preview */}
        {post.commentsCount > 0 && (
          <span>View all {post.commentsCount} comments</span>
        )}
      </div>
      <div className="post-timestamp">{formatDate(post.createdAt)}</div>
    </div>
  );
}

export default PostItem;
