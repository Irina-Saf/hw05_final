from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post, Comment

User = get_user_model()

POST_TITLE_LENGHT = 15


class PostModelTest(TestCase):
    """Создаем тестовые посты и пользователей."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Текст проверяемого поста больше 15 символов',
        )

    def test_post_models_have_correct_object_names(self):
        """Проверяем корректное имя поста."""

        post = PostModelTest.post
        expected_object_name = post.text[:POST_TITLE_LENGHT]
        self.assertEqual(str(post), expected_object_name)

    def test_models_have_verbose_name(self):
        """verbose_name в полях совпадает с ожидаемым."""
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст поста',
            'group': 'Группа'
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value)


class GroupModelTest(TestCase):
    """Создаем тестовые группы."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )

    def test_group_models_have_correct_object_names(self):
        """Проверяем корректное имя группы."""

        group = GroupModelTest.group
        expected_object_name = group.title
        self.assertEqual(expected_object_name, str(group))


class CommentModelTest(TestCase):
    """Создаем тестовый коммент."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.user_two = User.objects.create_user(username='UserComment')
        cls.post = Post.objects.create(
            author=cls.user_two,
            text='Текст поста',
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user_two,
            text='Текст комментария который очень длинный',
        )

    def test_comment_models_have_correct_object_names(self):
        """Проверяем корректное имена для комментария."""

        comment = CommentModelTest.comment
        self.assertEqual(
            comment._meta.get_field('text').verbose_name, 'Текст комментария')

        expected_object_name = comment.text[:POST_TITLE_LENGHT]
        self.assertEqual(str(comment), expected_object_name)
