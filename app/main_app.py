import time
from datetime import datetime
from functools import reduce

from flask import jsonify, Flask, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

from s3_service import create_presigned_url, PresignType

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:password@db:5432/pdb'
db = SQLAlchemy(app)

tags_posts = db.Table('tags_posts',
                      db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True),
                      db.Column('post_id', db.Integer, db.ForeignKey('posts.id'), primary_key=True)
                      )


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    raw = db.Column(db.String(128), nullable=True)
    remap = db.Column(db.String(128), nullable=True)
    ff = db.Column(db.String(128), nullable=True)
    raw_type = db.Column(db.String(128), nullable=True)
    remap_type = db.Column(db.String(128), nullable=True)
    ff_type = db.Column(db.String(128), nullable=True)
    raw_updated_at = db.Column(db.DateTime, nullable=True)
    remap_updated_at = db.Column(db.DateTime, nullable=True)
    ff_updated_at = db.Column(db.DateTime, nullable=True)
    tags = db.relationship('Tag', secondary=tags_posts, lazy='subquery',
                           back_populates='posts', cascade="delete")


class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128), nullable=False)
    posts = db.relationship('Post', secondary=tags_posts, lazy='subquery',
                            back_populates='tags', cascade="delete")
    parent_id = db.Column(db.Integer, db.ForeignKey('tags.id'))

    children = db.relationship('Tag', backref=db.backref('parent', remote_side=[id]), lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'children': [child.to_dict() for child in self.children]
        }


class Preset(db.Model):
    __tablename__ = 'preset'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
    key = db.Column(db.String(128))

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'key': self.key,
        }


with app.app_context():
    db.create_all()


def save_and_commit(obj):
    db.session.add(obj)
    db.session.commit()


def delete_and_commit(obj):
    db.session.delete(obj)
    db.session.commit()


@app.route('/')
def hello():
    return "Hello World! - Vadim"


@app.route('/tag', methods=['GET', 'POST', 'DELETE'])
def tag_routing():
    if request.method == 'GET':
        res = db.session.query(Tag).get(1)
        return jsonify([child.to_dict() for child in res.children])
    elif request.method == 'POST':
        data = request.get_json()
        name = data['name']
        parent_id = data['parentId']
        tag = Tag(name=name, parent_id=parent_id)
        save_and_commit(tag)
        return jsonify(tag.to_dict())
    elif request.method == 'DELETE':
        _id = request.args.get('id', -1)
        tag = db.session.query(Tag).get(_id)
        delete_and_commit(tag)
        return jsonify('true')


@app.route('/post', methods=['GET', 'POST', 'DELETE'])
def post():
    if request.method == 'GET':
        res = db.session.query(Post).all()
        return jsonify([r.to_dict() for r in res])
    elif request.method == 'POST':
        data = request.get_json()
        file_name = data['fileName']
        file_type = data['fileType']
        tags = data['tags']
        tags = db.session.query(Tag).filter(Tag.id.in_(tags)).all()
        tmst = int(time.time())
        _post = Post(ff=f'{tmst}.{file_name.rsplit(".", 1)[1]}', ff_type=file_type, ff_updated_at=datetime.utcnow())
        _post.tags = tags
        save_and_commit(_post)
        return jsonify({"file": create_presigned_url('file/' + _post.ff, file_type, PresignType.PUT.value),
                        "img": create_presigned_url('thum/' + f'{_post.ff.rsplit(".", 1)[0]}.jpg', 'image/jpeg',
                                                    PresignType.PUT.value)})
    elif request.method == 'DELETE':
        _id = request.args.get('id', -1, type=int)
        _post = db.session.query(Post).get(_id)
        save_and_commit(_post)
        return jsonify('true')


@app.route('/getPresign/bulk', methods=['POST'])
def get_bulk_presign():
    files = request.get_json()
    tags = Tag.query.filter(Tag.id.in_(files)).all()

    posts = [tag.posts for tag in tags]
    s = reduce(list.__add__, posts)
    urls = [create_presigned_url('file/' + _post.ff, _post.ff_type, PresignType.GET.value) for _post in s]
    return jsonify(urls)


@app.route('/preset', methods=['GET'])
def get_all_presets():
    presets = Preset.query.all()
    return jsonify([preset.to_dict() for preset in presets])


@app.route('/preset/<int:_id>', methods=['GET'])
def get_preset_download_url(_id):
    preset = Preset.query.get(_id)
    # print(preset.to_dict())
    # print(create_presigned_url('preset/' + preset.key, 'audio/mpeg', PresignType.GET.value))
    return create_presigned_url('preset/' + preset.key, 'audio/mpeg', PresignType.GET.value)


CORS(app)

if __name__ == '__main__':
    app.run(host="0.0.0.0", threaded=True)
