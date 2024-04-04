from datetime import datetime, timedelta
from sqlalchemy import func, case, extract
from collections import defaultdict

from app.extensions import db


tags_words = db.Table('tags_words',
            db.Column(
                'word_id', db.Integer(),
                db.ForeignKey('words.id', ondelete="CASCADE")
            ),
            db.Column(
                'tag_id',
                db.Integer(),
                db.ForeignKey('tags.id', ondelete="CASCADE")
            )
)


class TagModel(db.Model):
    __tablename__ = 'tags'
    
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    @classmethod
    def get_tag_by_id(cls, id_tage):
        tag = cls.query.filter_by(id=id_tage).first()
        return tag

    @classmethod
    def get_all_tags(cls):
        tags = cls.query.all()
        return tags

    @classmethod
    def create_tag(cls, data):
        tag = cls(name=data['name'])
        db.session.add(tag)
        db.session.commit()
        return tag

    @classmethod
    def delete_tag(cls, tag):
        db.session.delete(tag)
        db.session.commit()

    def __repr__(self):
        return '<Tag %r>' % self.name


class WordModel(db.Model):
    __tablename__ = "words"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    translation = db.Column(db.String(80), nullable=False)
    annotation = db.Column(db.Text)

    tags = db.relationship('TagModel',
        secondary=tags_words,
        backref=db.backref('words', lazy='dynamic')
    )

    @classmethod
    def get_word_by_id(cls, id_word):
        word = cls.query.filter_by(id=id_word).first()
        return word

    @classmethod
    def get_all_words(cls):
        words = cls.query.all()
        return words

    @classmethod
    def create_word(cls, data):
        annotation = data.get('annotation')
        word = cls(
            name=data['name'],
            translation=data['translation'],
            annotation=annotation
        )
        if 'tags' in data:
            tags = TagModel.query.filter(
                TagModel.id.in_(data['tags'])
            ).all()
            word.tags.extend(tags)

        db.session.add(word)
        db.session.commit()
        return word

    @classmethod
    def update_word(cls, id_word, data):
        word = cls.get_word_by_id(id_word)

        if 'name' in data:
            word.name = data['name']
        if 'translation' in data:
            word.translation = data['translation']
        if 'annotation' in data:
            word.annotation = data['annotation']
        if 'tags' in data:
            tags = TagModel.query.filter(
                TagModel.id.in_(data['tags'])
            ).all()
            word.tags.clear()
            word.tags = tags

        db.session.commit()
        return word

    @classmethod
    def delete_word(cls, word):
        db.session.delete(word)
        db.session.commit()

    def __repr__(self):
        return '<Word %r>' % self.name


sets_words = db.Table('sets_words',
            db.Column(
                'set_id', db.Integer(),
                db.ForeignKey('sets.id', ondelete="CASCADE")
            ),
            db.Column(
                'word_id',
                db.Integer(),
                db.ForeignKey('words.id', ondelete="CASCADE")
            )
)


class SetModel(db.Model):
    __tablename__ = "sets"

    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)

    words = db.relationship('WordModel',
        secondary=sets_words,
        backref=db.backref('sets', lazy='dynamic')
    )

    @classmethod
    def get_set_by_id(cls, id_set):
        set_words = cls.query.filter_by(id=id_set).first()
        return set_words

    @classmethod
    def get_all_sets(cls):
        sets = cls.query.all()
        return sets

    @classmethod
    def get_words_by_set_id(cls, set_id):
        words = db.session.query(WordModel).join(
            sets_words, (WordModel.id == sets_words.c.word_id)
        ).filter(
            sets_words.c.set_id == set_id
        ).all()

        return words


    @classmethod
    def create_set(cls, data):
        set_words = cls(
            name=data['name'],
        )
        if 'words' in data:
            words = WordModel.query.filter(
                WordModel.id.in_(data['words'])
            ).all()
            set_words.words.extend(words)

        db.session.add(set_words)
        db.session.commit()
        return set_words

    @classmethod
    def update_set(cls, id_set, data):
        set_words = cls.get_set_by_id(id_set)

        if 'name' in data:
            set_words.name = data['name']
        if 'words' in data:
            words = WordModel.query.filter(
                WordModel.id.in_(data['words'])
            ).all()
            set_words.words.clear()
            set_words.words = words

        db.session.commit()
        return set_words

    @classmethod
    def delete_set(cls, set_words):
        db.session.delete(set_words)
        db.session.commit()

    def __repr__(self):
        return '<Set %r>' % self.name


class HistoricHitsModel(db.Model):
    __tablename__ = "history_hits"
    today = datetime.utcnow().date()
    thirty_days_ago = today - timedelta(days=30)
    yesterday = today - timedelta(days=1)
    current_day = datetime.utcnow().day
    start_date_90days = yesterday - timedelta(days=90)

    id = db.Column(db.Integer(), primary_key=True)
    id_user = db.Column(db.Integer,
        db.ForeignKey('users.id', name='fk_historic_user_id_user'), nullable=False
    )
    id_word = db.Column(db.Integer,
        db.ForeignKey('words.id', name='fk_historic_word_id_word'), nullable=False
    )
    hit = db.Column(db.Boolean, nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.now)


    @classmethod
    def create_historics(cls, data, id_user):
        historics = []
        for row in data:
            historics.append(
                cls(
                    id_word=row['id_word'],
                    hit=row['hit'],
                    id_user=id_user,
                )
            )

        db.session.add_all(historics)
        db.session.commit()
        return historics

    @classmethod
    def get_historic_hits_by_user(cls, id_user):
        result = db.session.query(
            case(
                (cls.hit == True, 'hits'),
                else_='errors'
            ).label('hit_type'),
            func.count().label('count')
            ).filter(
                cls.date >= cls.thirty_days_ago,
                cls.date <= cls.yesterday,
                cls.id_user == id_user
        ).group_by(cls.hit).all()

        data = {'hits': 0, 'errors':0}
        for row in result:
            if row.hit_type == 'errors':
                data['errors'] = row.count
            else:
                data['hits'] = row.count

        return data

    @classmethod
    def get_historic_by_day_by_user(cls, id_user, date):
        result = db.session.query(
            case(
                (cls.hit == True, 'hits'),
                else_='errors'
            ).label('hit_type'),
            db.func.count().label('count')).filter(
            cls.date == date,
            cls.id_user == id_user
        ).group_by(cls.hit).all()
        return result

    @classmethod
    def get_historic_by_user_top10_words_error(cls, id_user):
        results = db.session.query(
            WordModel.name.label('word'),
            func.count().label('count')
        ).join(
            cls,
            WordModel.id == cls.id_word
        ).filter(
            cls.id_user == id_user,
            cls.hit == False,
            cls.date <= cls.yesterday
        ).group_by(
            WordModel.name
        ).order_by(
            func.count().desc()
        ).limit(10).all()

        return results

    @classmethod
    def get_historic_90days_by_user(cls, id_user):
        result = (
            db.session.query(
                case(
                    (cls.hit == True, 'hits'),
                    else_='errors'
                ).label('hit_type'),
                cls.date, 
                db.func.count().label('count')
            )
            .filter(
                cls.id_user == id_user,
                cls.date >= cls.start_date_90days,
                cls.date <= cls.yesterday
            )
            .group_by(cls.date,cls.hit).order_by(cls.date.asc())
            .all()
            )

        counts_by_date = defaultdict(dict)

        for row in result:
            date = row.date
            hit_type = row.hit_type
            count = row.count
            
            if date not in counts_by_date:
                counts_by_date[date] = {'hits': 0, 'errors': 0}
            
            counts_by_date[date][hit_type] = count

        output = [{'date': date, **counts} for date, counts in counts_by_date.items()]

        return output

    def __repr__(self):
        return '<Historic %r>' % self.id_user