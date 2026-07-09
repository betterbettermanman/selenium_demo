from datetime import datetime

from . import db


class UserAccount(db.Model):
    __tablename__ = 'user_account'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    website_code = db.Column(db.String(256), comment='网站编码')
    nick_name = db.Column(db.String(100), default='', comment='姓名')
    organ_name = db.Column(db.String(256), comment='单位名称')
    username = db.Column(db.String(100), nullable=False, comment='账号')
    password = db.Column(db.String(100), nullable=False, comment='密码')
    create_time = db.Column(db.DateTime, default=datetime.now, comment='创建日期')
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新日期')

    def to_dict(self):
        return {
            'id': self.id,
            'website_code': self.website_code,
            'nick_name': self.nick_name,
            'organ_name': self.organ_name,
            'username': self.username,
            'password': self.password,
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S') if self.create_time else None,
            'update_time': self.update_time.strftime('%Y-%m-%d %H:%M:%S') if self.update_time else None,
        }
