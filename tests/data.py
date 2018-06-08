from ResearchHelper.models import (
    User, InvitationCode, Post, Category, Tag, Series
)

def init(app, db):
    """Create tables if not exist"""
    with app.app_context():
        db.create_all(app=app)

def insert(app, db):
    """Insert data for testing."""
    # You must invoke database operation functions in appcontext.
    with app.app_context():
        invitation1 = InvitationCode(code='unused')
        invitation2 = InvitationCode(code='used12', assigned=True)
        db.session.add_all([invitation1, invitation2])

        # user(id=1)
        user = User(username='test', password='test', email='test@example.com')
        db.session.add(user)

        user1 = User(username='foo', password='foo', email='foo@example.com')
        user2 = User(username='bar', password='bar', email='bar@example.com')
        db.session.add_all([user1, user2])
        
        series1 = Series(name='Tutorial of Machine Learning')
        series2 = Series(name='Tutorial of Deep Learning')
        db.session.add_all([series1, series2])

        category1 = Category(name='machine learning')
        category2 = Category(name='deep learning')
        tag1 = Tag(name='ML')
        tag2 = Tag(name='DL')

        # post(id=1)
        post = Post(title='test title', body='test body')
        post.user = user
        db.session.add(post)

        post1 = Post(title='which is which', body='which is which?')
        post1.user = user1
        post1.series_id = series1.id
        post1.categories.append(category1)
        post1.tags.append(tag1)
        db.session.add(post1)
        
        post2 = Post(title='what is what', body='what is what?')
        post2.user = user2
        post2.series_id = series2.id
        post2.categories.append(category1)
        post2.categories.append(category2)
        post2.tags.append(tag1)
        post2.tags.append(tag2)
        db.session.add(post2)

        db.session.commit()