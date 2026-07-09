from models import db
from models.user_account import UserAccount


def sync_user_account_from_task(*, website_code, username, password, nick_name='', organ_name=None):
    """根据网站编码和账号同步用户表：不存在则新增，密码不一致则更新。"""
    if not website_code or not username or not password:
        return

    account = UserAccount.query.filter_by(
        website_code=website_code,
        username=username,
    ).first()

    if account is None:
        db.session.add(UserAccount(
            website_code=website_code,
            username=username,
            password=password,
            nick_name=nick_name or '',
            organ_name=organ_name,
        ))
    elif account.password != password:
        account.password = password
