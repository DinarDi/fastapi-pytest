from sqlalchemy import text

from src.database import User


async def test_user_create(session):
    user = User(
        username='Test user',
        email='test@mail.com',
    )
    session.add(user)
    await session.commit()

    data = await session.execute(text('SELECT id, username, email FROM "user" '))
    result = list(data)[0]
    assert isinstance(result[0], int)
    assert result[1] == 'Test user'
    assert result[2] == 'test@mail.com'
