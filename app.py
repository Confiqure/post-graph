import random
from flask import Flask, render_template, jsonify, request
from sqlalchemy import func
from database import SessionLocal
from models import Post, Category

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/random_uncategorized")
def random_uncategorized():
    session = SessionLocal()
    uncategorized_posts = session.query(Post).filter(Post.category_id == None).all()
    if not uncategorized_posts:
        return jsonify({"message": "No uncategorized posts found"}), 404

    post = random.choice(uncategorized_posts)
    data = {
        "id": post.id,
        "post_id": post.post_id,
        "content": post.content,
        "username": post.username,
        "post_url": post.post_url,
    }
    session.close()
    return jsonify(data)


@app.route("/categories")
def list_categories():
    """
    Returns a list of categories with their full paths, such as:
    "economy -> investing -> bitcoin"
    """
    session = SessionLocal()

    # Fetch all categories
    categories = session.query(Category).all()

    # Build a dictionary for easy lookup
    category_map = {c.id: c for c in categories}
    parent_map = {}  # Maps category ID to its parent ID
    for c in categories:
        parent_map[c.id] = c.parent_id

    # Function to recursively build full path
    def get_full_path(cat_id):
        path = []
        while cat_id is not None:
            cat = category_map[cat_id]
            path.insert(0, cat.name)  # Prepend category name
            cat_id = parent_map.get(cat_id)  # Move to parent
        return " → ".join(path)  # Return formatted path

    # Construct response data
    category_list = [
        {"id": c.id, "name": c.name, "full_path": get_full_path(c.id)}
        for c in categories
    ]

    session.close()
    return jsonify(category_list)


@app.route("/categories/json")
def categories_json():
    """
    Returns a hierarchical JSON of categories.
    If ?show_counts=true is in the query params, each category node will include
    a 'post_count' field indicating how many posts are directly in that category.
    """
    counts = {}
    session = SessionLocal()
    show_counts = request.args.get("show_counts", "").lower() == "true"
    root_categories = session.query(Category).filter(Category.parent_id == None).all()

    if show_counts:
        count_data = (
            session.query(Post.category_id, func.count(Post.id))
            .group_by(Post.category_id)
            .all()
        )
        counts = {cat_id: count for cat_id, count in count_data}

    def build_tree(category):
        node = {
            "id": category.id,
            "name": category.name,
            "children": [build_tree(sub) for sub in category.subcategories],
        }
        if show_counts:
            node["post_count"] = counts.get(category.id, 0)
        return node

    data = [build_tree(cat) for cat in root_categories]
    session.close()
    return jsonify(data)


@app.route("/assign_category", methods=["POST"])
def assign_category():
    """
    Assigns a category to a post based on the provided JSON payload.

    Expected JSON format:
    {
        "post_id": <int>,          # ID of the post
        "category_id": <int>        # ID of the category (nullable)
    }

    Returns:
    - 200 on success
    - 400 if data is missing/invalid
    - 404 if post or category not found
    """
    data = request.get_json()

    # Validate request data
    if not data or "post_id" not in data:
        return jsonify({"error": "Missing 'post_id'"}), 400

    post_id = data["post_id"]
    category_id = data.get("category_id")  # Can be None (uncategorized)

    session = SessionLocal()

    # Check if post exists
    post = session.query(Post).filter_by(id=post_id).first()
    if not post:
        session.close()
        return jsonify({"error": f"Post with ID {post_id} not found"}), 404

    # If category_id is provided, check if category exists
    if category_id is not None:
        category = session.query(Category).filter_by(id=category_id).first()
        if not category:
            session.close()
            return jsonify({"error": f"Category with ID {category_id} not found"}), 404

    # Assign the category (or remove it if None)
    post.category_id = category_id
    session.commit()
    session.close()

    return (
        jsonify({"message": f"Post {post_id} assigned to category {category_id}"}),
        200,
    )


if __name__ == "__main__":
    app.run(debug=True)
