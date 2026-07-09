from datetime import datetime

from . import db


class Website(db.Model):
    __tablename__ = 'website'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), default='', comment='网站名称')
    code = db.Column(db.String(100), comment='网站编码')
    url = db.Column(db.String(512), comment='网站URL')
    enable_sms_code = db.Column(db.String(8), default='0', comment='是否启用手机验证码（1：启用，0：不启用）')
    remark = db.Column(db.String(100), comment='备注')
    create_time = db.Column(db.DateTime, default=datetime.now, comment='创建日期')
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新日期')

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'code': self.code,
            'url': self.url,
            'enable_sms_code': self.enable_sms_code,
            'remark': self.remark,
            'create_time': self.create_time.strftime('%Y-%m-%d %H:%M:%S') if self.create_time else None,
            'update_time': self.update_time.strftime('%Y-%m-%d %H:%M:%S') if self.update_time else None,
        }
