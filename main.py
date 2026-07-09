"""
UmBala (UmBala) - детский тренажёр по школьным предметам Казахстана.
MVP: математика + чтение, 1-4 класс, интерфейс на ru/kk/en.

Запуск:
    pip install kivy kivymd
    python main.py
"""

from kivy.lang import Builder
import random
from kivy.properties import StringProperty, NumericProperty, ObjectProperty
from kivy.uix.screenmanager import Screen, ScreenManager, SlideTransition
from kivy.clock import Clock
from kivy.metrics import dp
from kivy.graphics import Color, Ellipse, Rectangle

from kivymd.app import MDApp
from kivymd.uix.card import MDCard
from kivymd.uix.button import MDRaisedButton, MDFlatButton
from kivymd.uix.label import MDLabel
from kivymd.uix.boxlayout import MDBoxLayout

import database
import content_loader
import gamification
from localization import tr, set_language, get_language, SUPPORTED_LANGUAGES
from creatures import CreatureWidget

database.init_db()

# Цвет кнопки-варианта ответа в обычном и выбранном состоянии.
OPTION_DEFAULT_COLOR = (0.90, 0.90, 0.94, 1)
OPTION_SELECTED_COLOR = (0.53, 0.47, 0.87, 1)
OPTION_DEFAULT_TEXT = (0.15, 0.15, 0.15, 1)
OPTION_SELECTED_TEXT = (1, 1, 1, 1)

from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.floatlayout import FloatLayout


from kivy.uix.relativelayout import RelativeLayout


class AvatarButton(ButtonBehavior, RelativeLayout):
    """Кликабельный аватар: базовая иконка + аксессуар в углу поверх неё.
    Виджет всегда пересоздаётся заново при обновлении экрана (а не мутирует
    свойство icon у уже отрисованного MDIconButton) - так KivyMD гарантированно
    перерисовывает иконку.

    ВАЖНО: используется именно RelativeLayout, а не FloatLayout. У FloatLayout
    дети без pos_hint позиционируются в АБСОЛЮТНЫХ координатах окна, а не
    относительно самого FloatLayout - из-за этого аватар с pos=(0,0) рисовался
    в углу всего окна, а не в углу своего контейнера. RelativeLayout сдвигает
    систему координат детей к своей собственной позиции - то, что нужно."""
    pass


def build_avatar_widget(avatar_species: str, accessory_icon: str = None, size_dp=44,
                         accent_color=(0.98, 0.78, 0.46, 1), animated=True):
    from kivymd.uix.label import MDIcon

    total = dp(size_dp)
    widget = AvatarButton(size_hint=(None, None), size=(total, total))

    creature = CreatureWidget(species=avatar_species, size_hint=(None, None), size=(total, total), pos=(0, 0))
    widget.add_widget(creature)

    if accessory_icon:
        badge = MDIcon(
            icon=accessory_icon,
            font_size=f"{int(size_dp * 0.4)}sp",
            theme_text_color="Custom",
            text_color=accent_color,
            pos_hint={"right": 1, "top": 1},
        )
        widget.add_widget(badge)

    widget.creature = creature
    if animated:
        _start_avatar_idle_animation(creature)
    return widget


def _start_avatar_idle_animation(creature):
    Animation.cancel_all(creature, "y")
    base_y = creature.y
    bob = (Animation(y=base_y + dp(5), duration=0.85, t="in_out_sine") +
           Animation(y=base_y, duration=0.85, t="in_out_sine"))
    bob.repeat = True
    bob.start(creature)


def play_avatar_trick(creature):
    """Небольшой "трюк" - кувырок с лёгким подпрыгиванием. Вызывается по тапу
    и время от времени сам по себе, чтобы аватар выглядел живым."""
    Animation.cancel_all(creature, "rotation", "scale_factor")
    creature.rotation = 0
    creature.scale_factor = 1.0
    trick = (
        Animation(rotation=360, scale_factor=1.2, duration=0.45, t="out_quad") +
        Animation(scale_factor=1.0, duration=0.15, t="out_back")
    )
    trick.start(creature)


from kivy.animation import Animation



KV = """
#:import dp kivy.metrics.dp

<WelcomeScreen>:
    name: "welcome"
    MDBoxLayout:
        orientation: "vertical"
        padding: dp(32)
        spacing: dp(16)
        MDLabel:
            text: "UmBala"
            font_style: "H4"
            halign: "center"
            size_hint_y: None
            height: dp(60)
        MDLabel:
            text: "Давай знакомиться! Как тебя зовут?"
            halign: "center"
            size_hint_y: None
            height: dp(30)
        MDTextField:
            id: name_field
            hint_text: "Имя"
            size_hint_x: 0.8
            pos_hint: {"center_x": 0.5}
        MDLabel:
            text: "Выбери класс:"
            halign: "center"
            size_hint_y: None
            height: dp(30)
        ScrollView:
            size_hint_y: None
            height: dp(48)
            do_scroll_y: False
            MDBoxLayout:
                id: grade_buttons
                size_hint_x: None
                width: self.minimum_width
                spacing: dp(8)
                padding: [dp(8), 0]
        Widget:
        MDRaisedButton:
            text: "Поехали!"
            pos_hint: {"center_x": 0.5}
            on_release: root.create_profile()

<HomeScreen>:
    name: "home"
    MDBoxLayout:
        orientation: "vertical"
        MDBoxLayout:
            orientation: "vertical"
            size_hint_y: None
            height: dp(190)
            padding: dp(16)
            spacing: dp(10)
            md_bg_color: 0.5, 0.47, 0.87, 1
            MDBoxLayout:
                spacing: dp(10)
                size_hint_y: None
                height: dp(64)
                MDBoxLayout:
                    id: avatar_container
                    size_hint: None, None
                    size: dp(64), dp(64)
                    padding: dp(4)
                    pos_hint: {"center_y": 0.5}
                    canvas.before:
                        Color:
                            rgba: 1, 1, 1, 1
                        Ellipse:
                            pos: self.pos
                            size: self.size
                MDLabel:
                    id: greeting_label
                    text: ""
                    theme_text_color: "Custom"
                    text_color: 1, 1, 1, 1
                    font_style: "H6"
                MDBoxLayout:
                    size_hint_x: None
                    width: dp(80)
                    MDIcon:
                        icon: "diamond-stone"
                        theme_text_color: "Custom"
                        text_color: 0.98, 0.78, 0.46, 1
                        pos_hint: {"center_y": 0.5}
                        size_hint_x: None
                        width: dp(24)
                    MDLabel:
                        id: coins_label
                        text: ""
                        theme_text_color: "Custom"
                        text_color: 1, 1, 1, 1
                        halign: "left"
            MDLabel:
                id: level_label
                text: ""
                theme_text_color: "Custom"
                text_color: 1, 1, 1, 1
                size_hint_y: None
                height: dp(24)
            MDProgressBar:
                id: xp_bar
                value: 0
                color: 0.98, 0.78, 0.46, 1
            MDCard:
                id: quest_card
                size_hint_y: None
                height: dp(56)
                spacing: dp(12)
                padding: [dp(10), dp(8)]
                radius: [16, 16, 16, 16]
                md_bg_color: 0.98, 0.91, 0.85, 1
                MDBoxLayout:
                    size_hint: None, None
                    size: dp(40), dp(40)
                    pos_hint: {"center_y": 0.5}
                    canvas.before:
                        Color:
                            rgba: 0.94, 0.62, 0.42, 1
                        Ellipse:
                            pos: self.pos
                            size: self.size
                    MDIcon:
                        id: quest_icon
                        icon: "castle"
                        theme_text_color: "Custom"
                        text_color: 1, 1, 1, 1
                        pos_hint: {"center_x": 0.5, "center_y": 0.5}
                        halign: "center"
                MDLabel:
                    id: quest_label
                    text: ""
                    theme_text_color: "Custom"
                    text_color: 0.35, 0.22, 0.15, 1
        ScrollView:
            BoxLayout:
                id: content_box
                orientation: "vertical"
                padding: dp(16)
                spacing: dp(12)
                size_hint_y: None
                height: max(self.minimum_height, dp(420))
                MDLabel:
                    text: root.tr_subjects
                    font_style: "Subtitle1"
                    size_hint_y: None
                    height: dp(28)
                MDGridLayout:
                    id: subject_grid
                    cols: 2
                    spacing: dp(12)
                    size_hint_y: None
                    height: self.minimum_height
        MDBoxLayout:
            size_hint_y: None
            height: dp(56)
            MDIconButton:
                icon: "home"
                pos_hint: {"center_y": 0.5}
            MDIconButton:
                icon: "cart"
                pos_hint: {"center_y": 0.5}
                on_release: root.go_shop()
            MDIconButton:
                icon: "treasure-chest"
                pos_hint: {"center_y": 0.5}
                on_release: root.go_inventory()
            MDIconButton:
                icon: "account"
                pos_hint: {"center_y": 0.5}
                on_release: root.go_profile()
            MDIconButton:
                icon: "cog"
                pos_hint: {"center_y": 0.5}
                on_release: root.go_profile()

<TopicListScreen>:
    name: "topics"
    MDBoxLayout:
        orientation: "vertical"
        MDTopAppBar:
            id: topbar
            title: ""
            left_action_items: [["arrow-left", lambda x: root.go_back()]]
        ScrollView:
            MDBoxLayout:
                id: topics_box
                orientation: "vertical"
                padding: dp(16)
                spacing: dp(10)
                size_hint_y: None
                height: self.minimum_height

<LessonScreen>:
    name: "lesson"
    MDBoxLayout:
        orientation: "vertical"
        padding: dp(20)
        spacing: dp(16)
        MDLabel:
            id: progress_label
            text: ""
            size_hint_y: None
            height: dp(24)
        MDCard:
            id: passage_card
            padding: dp(20)
            radius: [20, 20, 20, 20]
            size_hint_y: None
            height: dp(0)
            opacity: 0
            md_bg_color: 0.9, 0.95, 0.93, 1
            MDLabel:
                id: passage_label
                text: ""
        MDLabel:
            id: question_label
            text: ""
            font_style: "H6"
            size_hint_y: None
            height: dp(60)
        MDTextField:
            id: answer_field
            hint_text: "Ответ"
            size_hint_x: 0.6
            pos_hint: {"center_x": 0.5}
            font_size: "22sp"
            foreground_color: 0.1, 0.1, 0.15, 1
            theme_text_color: "Custom"
            text_color_normal: 0.1, 0.1, 0.15, 1
            text_color_focus: 0.1, 0.1, 0.15, 1
            halign: "center"
        MDBoxLayout:
            id: options_box
            orientation: "vertical"
            spacing: dp(10)
            size_hint_y: None
            height: self.minimum_height
        Widget:
        MDLabel:
            id: feedback_label
            text: ""
            halign: "center"
            size_hint_y: None
            height: dp(30)
        MDRaisedButton:
            id: check_button
            text: ""
            pos_hint: {"center_x": 0.5}
            on_release: root.check_answer()

<ProfileScreen>:
    name: "profile"
    MDBoxLayout:
        orientation: "vertical"
        MDTopAppBar:
            title: ""
            left_action_items: [["arrow-left", lambda x: root.go_back()]]
        MDBoxLayout:
            orientation: "vertical"
            padding: dp(24)
            spacing: dp(12)
            MDBoxLayout:
                id: profile_avatar_container
                size_hint: None, None
                size: dp(90), dp(90)
                pos_hint: {"center_x": 0.5}
            MDLabel:
                id: stats_label
                text: ""
                halign: "center"
            MDLabel:
                text: "Язык / Тіл / Language"
                size_hint_y: None
                height: dp(30)
            MDBoxLayout:
                id: lang_buttons
                size_hint_y: None
                height: dp(48)
                spacing: dp(8)
            MDLabel:
                id: grade_section_label
                text: ""
                size_hint_y: None
                height: dp(30)
            ScrollView:
                size_hint_y: None
                height: dp(48)
                do_scroll_y: False
                MDBoxLayout:
                    id: grade_buttons
                    size_hint_x: None
                    width: self.minimum_width
                    spacing: dp(8)
                    padding: [dp(8), 0]

<InventoryScreen>:
    name: "inventory"
    MDBoxLayout:
        orientation: "vertical"
        MDTopAppBar:
            id: inventory_topbar
            title: ""
            left_action_items: [["arrow-left", lambda x: root.go_back()]]
        ScrollView:
            MDBoxLayout:
                id: inventory_box
                orientation: "vertical"
                padding: dp(16)
                spacing: dp(16)
                size_hint_y: None
                height: self.minimum_height

<ShopScreen>:
    name: "shop"
    MDBoxLayout:
        orientation: "vertical"
        MDTopAppBar:
            id: shop_topbar
            title: ""
            left_action_items: [["arrow-left", lambda x: root.go_back()]]
            right_action_items: [["diamond-stone", lambda x: None]]
        MDBoxLayout:
            size_hint_y: None
            height: dp(36)
            padding: [dp(16), 0]
            MDIcon:
                icon: "diamond-stone"
                theme_text_color: "Custom"
                text_color: 0.85, 0.6, 0.1, 1
                size_hint_x: None
                width: dp(24)
            MDLabel:
                id: shop_coins_label
                text: ""
                bold: True
        ScrollView:
            MDBoxLayout:
                id: shop_box
                orientation: "vertical"
                padding: dp(16)
                spacing: dp(16)
                size_hint_y: None
                height: self.minimum_height
"""


class WelcomeScreen(Screen):
    selected_grade = NumericProperty(1)

    def on_kv_post(self, base_widget):
        self.ids.grade_buttons.clear_widgets()
        for g in range(1, 12):
            btn = MDFlatButton(text=str(g), size_hint_x=None, width=dp(44),
                                on_release=lambda inst, gg=g: self.pick_grade(gg))
            self.ids.grade_buttons.add_widget(btn)

    def pick_grade(self, grade):
        self.selected_grade = grade

    def create_profile(self):
        name = self.ids.name_field.text.strip() or "Друг"
        profile_id = database.create_profile(name=name, grade=self.selected_grade, language=get_language())
        app = MDApp.get_running_app()
        app.profile_id = profile_id
        app.go_home()


class HomeScreen(Screen):
    tr_subjects = StringProperty("")
    room_color = ObjectProperty([0.96, 0.97, 0.95, 1])

    def on_kv_post(self, base_widget):
        self._room_rect = None
        self.ids.content_box.bind(pos=self._sync_room_rect, size=self._sync_room_rect)

    def _sync_room_rect(self, instance, value):
        if self._room_rect is not None:
            self._room_rect.pos = instance.pos
            self._room_rect.size = instance.size

    def _apply_room_background(self):
        """Полностью пересоздаём canvas-инструкции фона (а не мутируем свойство
        уже отрисованного виджета) - в этой версии KivyMD только так гарантированно
        обновляется картинка после возврата с другого экрана."""
        from kivy.graphics import Color, Rectangle
        content_box = self.ids.content_box
        content_box.canvas.before.clear()
        with content_box.canvas.before:
            Color(*self.room_color)
            self._room_rect = Rectangle(pos=content_box.pos, size=content_box.size)

    def on_pre_enter(self, *args):
        self.refresh()

    def on_leave(self, *args):
        # Останавливаем ротацию реплик, пока экран не виден - нет смысла
        # обновлять текст виджета, который сейчас не отображается.
        event = getattr(self, "_idle_event", None)
        if event:
            event.cancel()
        avatar_event = getattr(self, "_avatar_trick_event", None)
        if avatar_event:
            avatar_event.cancel()

    def refresh(self):
        app = MDApp.get_running_app()
        profile = database.get_profile(app.profile_id)
        self.tr_subjects = tr("subjects")
        self.ids.greeting_label.text = tr("home_greeting", name=profile["name"])
        self.ids.coins_label.text = str(profile["coins"])
        self.ids.level_label.text = f"{tr('level')} {profile['level']}  ·  {profile['xp']}/{profile['level']*100} XP"
        self.ids.xp_bar.value = (profile["xp"] / (profile["level"] * 100)) * 100
        self.ids.avatar_container.clear_widgets()
        avatar_icon = self._avatar_to_mdi(profile["avatar"])
        accessory_icon = self._accessory_to_mdi(profile["equipped_accessory"])
        avatar_widget = build_avatar_widget(avatar_icon, accessory_icon, size_dp=56)
        avatar_widget.bind(on_release=lambda inst: app.open_shop())
        self.ids.avatar_container.add_widget(avatar_widget)
        self._avatar_widget = avatar_widget

        avatar_event = getattr(self, "_avatar_trick_event", None)
        if avatar_event:
            avatar_event.cancel()
        self._avatar_trick_event = Clock.schedule_interval(
            lambda dt: play_avatar_trick(self._avatar_widget.creature), 18
        )

        self.room_color = self._room_to_color(profile["equipped_room"])
        self._apply_room_background()

        # "Квест дня" - берём первую незавершённую тему по математике для класса ребёнка.
        topics = content_loader.get_topics("math", profile["grade"])
        done_ids = {p["topic_id"] for p in database.get_subject_progress(app.profile_id, "math") if p["stars"] > 0}
        next_topic = next((t for t in topics if t["topic_id"] not in done_ids), topics[0] if topics else None)
        if next_topic:
            self.ids.quest_icon.icon = next_topic["quest_icon"]
            title = next_topic["title"].get(get_language(), next_topic["title"]["ru"])
            self.ids.quest_label.text = f"{tr('todays_quest')}: {title}"
        else:
            self.ids.quest_label.text = tr("todays_quest")

        self.ids.subject_grid.clear_widgets()
        subjects = [
            ("math", tr("subject_math"), "calculator-variant", (0.85, 0.95, 0.88, 1), (0.25, 0.55, 0.35, 1)),
            ("reading", tr("subject_reading"), "book-open-page-variant", (0.86, 0.9, 0.98, 1), (0.2, 0.35, 0.65, 1)),
            ("kazakh", tr("subject_kazakh"), "translate", (0.98, 0.9, 0.85, 1), (0.65, 0.35, 0.15, 1)),
            ("english", tr("subject_english"), "alphabetical-variant", (0.95, 0.88, 0.98, 1), (0.5, 0.25, 0.6, 1)),
            ("world",
             tr("subject_world_science") if profile["grade"] >= 5 else tr("subject_world"),
             "earth", (0.88, 0.96, 0.96, 1), (0.15, 0.5, 0.5, 1)),
        ]
        for subject_key, subject_label, icon, badge_color, accent_color in subjects:
            topics = content_loader.get_topics(subject_key, profile["grade"])
            done = len({p["topic_id"] for p in database.get_subject_progress(app.profile_id, subject_key) if p["stars"] > 0})
            total = len(topics) or 1
            progress_fraction = done / total

            tile = MDCard(orientation="vertical", padding=12, spacing=6,
                           size_hint_y=None, height=dp(128), radius=[18, 18, 18, 18],
                           ripple_behavior=True, md_bg_color=(0.97, 0.97, 0.99, 1))
            from kivymd.uix.label import MDIcon

            icon_badge = MDBoxLayout(size_hint=(None, None), size=(dp(44), dp(44)), pos_hint={"center_x": 0.5})
            with icon_badge.canvas.before:
                Color(*badge_color)
                badge_ellipse = Ellipse(pos=icon_badge.pos, size=icon_badge.size)

            def _sync_badge_ellipse(inst, val, ellipse=badge_ellipse):
                ellipse.pos = inst.pos
                ellipse.size = inst.size

            icon_badge.bind(pos=_sync_badge_ellipse, size=_sync_badge_ellipse)
            icon_widget = MDIcon(icon=icon, halign="center", theme_text_color="Custom",
                                  text_color=accent_color, font_size="26sp",
                                  pos_hint={"center_x": 0.5, "center_y": 0.5})
            icon_badge.add_widget(icon_widget)
            tile.add_widget(icon_badge)

            tile.add_widget(MDLabel(text=subject_label, halign="center", size_hint_y=None, height=dp(24)))

            bar_bg = MDBoxLayout(size_hint_y=None, height=dp(6))
            with bar_bg.canvas.before:
                Color(0.88, 0.88, 0.9, 1)
                bg_rect = Rectangle(pos=bar_bg.pos, size=bar_bg.size)
                Color(*accent_color)
                fill_rect = Rectangle(pos=bar_bg.pos, size=(bar_bg.width * progress_fraction, bar_bg.height))

            def _sync_bar(inst, val, bg_rect=bg_rect, fill_rect=fill_rect, frac=progress_fraction):
                bg_rect.pos = inst.pos
                bg_rect.size = inst.size
                fill_rect.pos = inst.pos
                fill_rect.size = (inst.width * frac, inst.height)

            bar_bg.bind(pos=_sync_bar, size=_sync_bar)
            tile.add_widget(bar_bg)

            progress_label = MDLabel(text=f"{done}/{total}", halign="center", font_size="11sp",
                                      size_hint_y=None, height=dp(16))
            tile.add_widget(progress_label)

            tile.bind(on_release=lambda inst, s=subject_key, g=profile["grade"]: app.open_topics(s, g))
            self.ids.subject_grid.add_widget(tile)

    @staticmethod
    def _avatar_to_mdi(avatar_value: str) -> str:
        """avatar в БД хранит имя иконки напрямую (после покупки в магазине)."""
        catalog = content_loader.get_shop_catalog()
        for item in catalog["avatars"]:
            if item["item_id"] == avatar_value or item["icon"] == avatar_value:
                return item["icon"]
        return "account"

    @staticmethod
    def _accessory_to_mdi(accessory_value):
        if not accessory_value:
            return None
        catalog = content_loader.get_shop_catalog()
        for item in catalog["accessories"]:
            if item["item_id"] == accessory_value or item["icon"] == accessory_value:
                return item["icon"]
        return None

    @staticmethod
    def _room_to_color(room_value):
        catalog = content_loader.get_shop_catalog()
        for item in catalog.get("rooms", []):
            if item["item_id"] == room_value:
                return item["color"]
        return [0.96, 0.97, 0.95, 1]

    def go_profile(self):
        MDApp.get_running_app().root.current = "profile"

    def go_shop(self):
        MDApp.get_running_app().open_shop()

    def go_inventory(self):
        MDApp.get_running_app().open_inventory()


class TopicListScreen(Screen):
    subject = StringProperty("")
    grade = NumericProperty(1)

    def open_for(self, subject, grade):
        self.subject = subject
        self.grade = grade
        if subject == "world" and grade >= 5:
            self.ids.topbar.title = tr("subject_world_science")
        else:
            self.ids.topbar.title = tr(f"subject_{subject}")
        self.ids.topics_box.clear_widgets()

        app = MDApp.get_running_app()
        progress_rows = {p["topic_id"]: p for p in database.get_subject_progress(app.profile_id, subject)}
        topics = content_loader.get_topics(subject, grade)

        if not topics:
            self.ids.topics_box.add_widget(MDLabel(
                text=tr("no_topics_yet"), halign="center",
                theme_text_color="Custom", text_color=(0.5, 0.5, 0.5, 1),
                size_hint_y=None, height=dp(80),
            ))
            return

        from kivymd.uix.label import MDIcon
        previous_completed = True  # первый уровень в классе всегда открыт
        for level_num, topic in enumerate(topics, start=1):
            title = topic["title"].get(get_language(), topic["title"]["ru"])
            prog = progress_rows.get(topic["topic_id"])
            star_count = prog["stars"] if prog else 0
            is_completed = star_count > 0
            is_unlocked = previous_completed

            row_card = MDCard(orientation="horizontal", size_hint_y=None, height=dp(68),
                               padding=dp(12), spacing=dp(12), radius=[16, 16, 16, 16],
                               ripple_behavior=is_unlocked,
                               md_bg_color=(0.95, 0.97, 0.95, 1) if is_unlocked else (0.90, 0.90, 0.90, 1))

            if is_unlocked:
                row_card.add_widget(MDIcon(icon=topic["quest_icon"], size_hint_x=None, width=dp(32),
                                            theme_text_color="Custom", text_color=(0.33, 0.29, 0.72, 1)))
            else:
                row_card.add_widget(MDIcon(icon="lock", size_hint_x=None, width=dp(32),
                                            theme_text_color="Custom", text_color=(0.6, 0.6, 0.6, 1)))

            label_box = MDBoxLayout(orientation="vertical")
            level_label = MDLabel(
                text=f"{tr('level_word')} {level_num}", font_size="11sp",
                theme_text_color="Custom",
                text_color=(0.5, 0.5, 0.5, 1) if is_unlocked else (0.65, 0.65, 0.65, 1),
                size_hint_y=None, height=dp(16),
            )
            title_label = MDLabel(
                text=title,
                theme_text_color="Custom",
                text_color=(0.15, 0.15, 0.18, 1) if is_unlocked else (0.6, 0.6, 0.6, 1),
            )
            label_box.add_widget(level_label)
            label_box.add_widget(title_label)
            row_card.add_widget(label_box)

            if is_unlocked:
                stars_box = MDBoxLayout(size_hint_x=None, width=dp(90), spacing=dp(2))
                for i in range(3):
                    star_icon = "star" if i < star_count else "star-outline"
                    stars_box.add_widget(MDIcon(icon=star_icon, theme_text_color="Custom",
                                                 text_color=(0.85, 0.6, 0.1, 1), font_size="18sp"))
                row_card.add_widget(stars_box)
                row_card.bind(on_release=lambda inst, t=topic: app.open_lesson(subject, grade, t["topic_id"]))
            else:
                hint_label = MDLabel(text=tr("locked_hint"), font_size="10sp", halign="right",
                                      theme_text_color="Custom", text_color=(0.65, 0.65, 0.65, 1),
                                      size_hint_x=None, width=dp(90))
                row_card.add_widget(hint_label)

            self.ids.topics_box.add_widget(row_card)
            previous_completed = is_completed

    def go_back(self):
        MDApp.get_running_app().root.current = "home"


class LessonScreen(Screen):
    subject = StringProperty("")
    grade = NumericProperty(1)
    topic_id = StringProperty("")

    SESSION_SIZE = 8  # сколько заданий даём за один заход в тему - не весь банк разом

    def open_for(self, subject, grade, topic_id):
        self.subject = subject
        self.grade = grade
        self.topic_id = topic_id
        self.topic = content_loader.get_topic(subject, grade, topic_id)
        bank = self.topic["tasks"]
        session_size = min(self.SESSION_SIZE, len(bank))
        self.tasks = random.sample(bank, session_size)
        self.index = 0
        self.correct_count = 0
        self.attempts_current = 0
        self.selected_option = None
        self.selected_button = None
        self.option_buttons = []
        self.show_task()

    def show_task(self):
        self.attempts_current = 0
        self.selected_option = None
        self.selected_button = None
        self.option_buttons = []
        self.ids.feedback_label.text = ""
        task = self.tasks[self.index]
        self.ids.progress_label.text = tr("task_of", current=self.index + 1, total=len(self.tasks))
        self.ids.question_label.text = task["question"].get(get_language(), task["question"]["ru"])
        self.ids.check_button.text = tr("check_answer")
        self.ids.check_button.disabled = False

        passage = task.get("passage")
        if passage:
            self.ids.passage_label.text = passage.get(get_language(), passage["ru"])
            self.ids.passage_card.height = dp(120)
            self.ids.passage_card.opacity = 1
        else:
            self.ids.passage_label.text = ""
            self.ids.passage_card.height = 0
            self.ids.passage_card.opacity = 0

        self.ids.options_box.clear_widgets()
        self.ids.answer_field.text = ""

        if task["type"] in ("choice", "passage_choice"):
            self.ids.answer_field.opacity = 0
            self.ids.answer_field.disabled = True
            self.ids.answer_field.size_hint_y = None
            self.ids.answer_field.height = 0
            for opt in task["options"]:
                btn = MDRaisedButton(
                    text=str(opt),
                    pos_hint={"center_x": 0.5},
                    md_bg_color=OPTION_DEFAULT_COLOR,
                    text_color=OPTION_DEFAULT_TEXT,
                )
                btn.bind(on_release=lambda inst, o=opt: self.select_option(o, inst))
                self.ids.options_box.add_widget(btn)
                self.option_buttons.append(btn)
        else:
            self.ids.answer_field.opacity = 1
            self.ids.answer_field.disabled = False
            self.ids.answer_field.size_hint_y = None
            self.ids.answer_field.height = dp(48)

    def select_option(self, option, button_widget):
        # Сбрасываем подсветку предыдущего выбранного варианта.
        if self.selected_button is not None:
            self.selected_button.md_bg_color = OPTION_DEFAULT_COLOR
            self.selected_button.text_color = OPTION_DEFAULT_TEXT
        # Подсвечиваем текущий выбор - именно этого не хватало.
        button_widget.md_bg_color = OPTION_SELECTED_COLOR
        button_widget.text_color = OPTION_SELECTED_TEXT
        self.selected_option = option
        self.selected_button = button_widget

    def check_answer(self):
        task = self.tasks[self.index]
        self.attempts_current += 1

        if task["type"] in ("choice", "passage_choice"):
            given = self.selected_option
        else:
            given = self.ids.answer_field.text.strip()
            try:
                given = int(given)
            except ValueError:
                pass

        is_correct = (given == task["correct"])
        app = MDApp.get_running_app()

        if is_correct:
            self.ids.feedback_label.text = tr("correct")
            if self.selected_button is not None:
                self.selected_button.md_bg_color = (0.4, 0.75, 0.45, 1)
                self.selected_button.text_color = (1, 1, 1, 1)
            self.ids.check_button.disabled = True
            reward = gamification.reward_for_answer(True, self.attempts_current)
            database.add_rewards(app.profile_id, coins=reward["coins"], xp=reward["xp"])
            database.record_answer(app.profile_id, task["task_id"], True)
            self.correct_count += 1
            Clock.schedule_once(lambda dt: self.next_task(), 0.8)
        else:
            self.ids.feedback_label.text = tr("try_again")
            if self.selected_button is not None:
                self.selected_button.md_bg_color = (0.85, 0.4, 0.35, 1)
                self.selected_button.text_color = (1, 1, 1, 1)
            database.record_answer(app.profile_id, task["task_id"], False)

    def next_task(self):
        self.index += 1
        if self.index >= len(self.tasks):
            self.finish_topic()
        else:
            self.show_task()

    def finish_topic(self):
        app = MDApp.get_running_app()
        result = gamification.reward_for_topic_completion(self.correct_count, len(self.tasks))
        database.add_rewards(app.profile_id, coins=result["coins"], xp=result["xp"])
        database.update_topic_progress(app.profile_id, self.subject, self.topic_id,
                                        self.correct_count, len(self.tasks), result["stars"])
        if self.correct_count == len(self.tasks):
            database.grant_achievement(app.profile_id, "topic_master")
        app.root.current = "home"


class ProfileScreen(Screen):
    def on_pre_enter(self, *args):
        app = MDApp.get_running_app()
        profile = database.get_profile(app.profile_id)
        self.ids.stats_label.text = (
            f"{profile['name']} · {tr('grade')} {profile['grade']}\n"
            f"{tr('level')} {profile['level']} · {profile['coins']} монет"
        )
        self.ids.profile_avatar_container.clear_widgets()
        avatar_icon = HomeScreen._avatar_to_mdi(profile["avatar"])
        accessory_icon = HomeScreen._accessory_to_mdi(profile["equipped_accessory"])
        avatar_widget = build_avatar_widget(avatar_icon, accessory_icon, size_dp=110)
        self.ids.profile_avatar_container.add_widget(avatar_widget)
        self.ids.lang_buttons.clear_widgets()
        for code, label in (("ru", "Русский"), ("kk", "Қазақша"), ("en", "English")):
            btn = MDFlatButton(text=label, on_release=lambda inst, c=code: self.switch_language(c))
            self.ids.lang_buttons.add_widget(btn)

        self.ids.grade_section_label.text = f"{tr('grade')} (1-11)"
        self.ids.grade_buttons.clear_widgets()
        for g in range(1, 12):
            is_current = g == profile["grade"]
            btn = MDRaisedButton(text=str(g), size_hint_x=None, width=dp(44)) if is_current \
                else MDFlatButton(text=str(g), size_hint_x=None, width=dp(44))
            if not is_current:
                btn.bind(on_release=lambda inst, gg=g: self.switch_grade(gg))
            self.ids.grade_buttons.add_widget(btn)

    def switch_grade(self, grade):
        app = MDApp.get_running_app()
        database.update_grade(app.profile_id, grade)
        self.on_pre_enter()

    def switch_language(self, code):
        set_language(code)
        MDApp.get_running_app().root.current = "home"

    def go_back(self):
        MDApp.get_running_app().root.current = "home"


def _equipped_value(profile, kind, item):
    if kind == "avatar":
        return profile["avatar"] == item["icon"]
    if kind == "accessory":
        return profile["equipped_accessory"] == item["icon"]
    if kind == "room":
        return profile["equipped_room"] == item["item_id"]
    return False


def build_item_preview(item, kind):
    from kivymd.uix.label import MDIcon
    if kind == "room":
        from kivy.uix.anchorlayout import AnchorLayout
        from kivy.uix.widget import Widget
        from kivy.graphics import Color, RoundedRectangle

        wrapper = AnchorLayout(size_hint_y=None, height=dp(40))
        swatch = Widget(size_hint=(None, None), size=(dp(64), dp(36)))
        color = item["color"]
        with swatch.canvas:
            Color(*color)
            rect = RoundedRectangle(pos=swatch.pos, size=swatch.size, radius=[10])

        def _sync(instance, _value):
            rect.pos = instance.pos
            rect.size = instance.size

        swatch.bind(pos=_sync, size=_sync)
        wrapper.add_widget(swatch)
        return wrapper
    return MDIcon(icon=item["icon"], halign="center", font_size="36sp",
                   theme_text_color="Custom", text_color=(0.33, 0.29, 0.72, 1))


def build_item_card(item, kind, is_owned, is_equipped, on_buy=None, on_equip=None, on_unequip=None):
    """Карточка товара, общая для магазина и инвентаря.
    on_buy/on_equip/on_unequip - колбэки без аргументов (уже забинженные снаружи)."""
    from kivymd.uix.label import MDIcon

    card = MDCard(orientation="vertical", padding=dp(10), spacing=dp(6),
                   size_hint_y=None, height=dp(150), radius=[16, 16, 16, 16],
                   md_bg_color=(0.95, 0.96, 0.99, 1) if not is_equipped else (0.85, 0.95, 0.88, 1))

    card.add_widget(build_item_preview(item, kind))
    name = item["name"].get(get_language(), item["name"]["ru"])
    card.add_widget(MDLabel(text=name, halign="center", size_hint_y=None, height=dp(24)))

    price_row = MDBoxLayout(size_hint_y=None, height=dp(22), spacing=dp(4))
    is_free = item["price"] == 0
    if is_free:
        price_row.add_widget(MDLabel(text=tr("free"), halign="center", font_size="12sp"))
    else:
        price_row.add_widget(MDIcon(icon="diamond-stone", size_hint_x=None, width=dp(16),
                                     theme_text_color="Custom", text_color=(0.85, 0.6, 0.1, 1)))
        price_row.add_widget(MDLabel(text=str(item["price"]), font_size="12sp"))
    card.add_widget(price_row)

    if is_equipped:
        if on_unequip is not None:
            btn = MDRaisedButton(text=tr("unequip"), pos_hint={"center_x": 0.5})
            btn.bind(on_release=lambda inst: on_unequip())
        else:
            btn = MDFlatButton(text=tr("equipped"), disabled=True, pos_hint={"center_x": 0.5})
    elif is_owned:
        btn = MDRaisedButton(text=tr("equip"), pos_hint={"center_x": 0.5})
        btn.bind(on_release=lambda inst: on_equip())
    else:
        btn = MDRaisedButton(text=tr("buy"), pos_hint={"center_x": 0.5})
        btn.bind(on_release=lambda inst: on_buy())
    card.add_widget(btn)
    return card


SHOP_CATEGORIES = [
    ("avatars", "avatar", True),        # (catalog_key, kind, allow_unequip)
    ("accessories", "accessory", False),
    ("rooms", "room", True),
]
# allow_unequip здесь означает наоборот "нельзя снять совсем" для avatar/room -
# см. использование ниже: только accessory реально может быть снят в "никакой".


class ShopScreen(Screen):
    def on_pre_enter(self, *args):
        self.refresh()

    def refresh(self):
        app = MDApp.get_running_app()
        profile = database.get_profile(app.profile_id)
        self.ids.shop_topbar.title = tr("shop")
        self.ids.shop_coins_label.text = str(profile["coins"])
        self.ids.shop_box.clear_widgets()

        owned_ids = database.get_owned_item_ids(app.profile_id)
        catalog = content_loader.get_shop_catalog()

        for catalog_key, kind, _ in SHOP_CATEGORIES:
            items = catalog.get(catalog_key, [])
            if not items:
                continue
            self.ids.shop_box.add_widget(self._section_label(tr(catalog_key)))
            self.ids.shop_box.add_widget(self._build_grid(items, kind, owned_ids, profile))

    @staticmethod
    def _section_label(text):
        return MDLabel(text=text, font_style="Subtitle1", size_hint_y=None, height=dp(28))

    def _build_grid(self, items, kind, owned_ids, profile):
        from kivymd.uix.gridlayout import MDGridLayout

        grid = MDGridLayout(cols=2, spacing=dp(10), size_hint_y=None, adaptive_height=True)
        for item in items:
            is_free = item["price"] == 0
            is_owned = is_free or item["item_id"] in owned_ids
            is_equipped = _equipped_value(profile, kind, item)
            can_unequip = is_equipped and kind == "accessory"

            card = build_item_card(
                item, kind, is_owned, is_equipped,
                on_buy=lambda it=item, k=kind: self.buy(it, k),
                on_equip=lambda it=item, k=kind: self.equip(it, k),
                on_unequip=(lambda: self.unequip_accessory()) if can_unequip else None,
            )
            grid.add_widget(card)
        return grid

    def buy(self, item, kind):
        app = MDApp.get_running_app()
        result = database.purchase_item(app.profile_id, item["item_id"], item["price"])
        if result == "ok":
            self.equip(item, kind)
        elif result == "not_enough_coins":
            self.ids.shop_coins_label.text = f"{tr('not_enough_coins')}!"
            Clock.schedule_once(lambda dt: self.refresh(), 1.2)

    def equip(self, item, kind):
        app = MDApp.get_running_app()
        if kind == "avatar":
            database.equip_avatar(app.profile_id, item["icon"])
        elif kind == "accessory":
            database.equip_accessory(app.profile_id, item["icon"])
        elif kind == "room":
            database.equip_room(app.profile_id, item["item_id"])
        self.refresh()

    def unequip_accessory(self):
        app = MDApp.get_running_app()
        database.unequip_accessory(app.profile_id)
        self.refresh()

    def go_back(self):
        MDApp.get_running_app().root.current = "home"


class InventoryScreen(Screen):
    """То же самое, что и магазин, но показывает только уже купленные вещи
    и без кнопки 'Купить' - только переключение экипировки."""

    def on_pre_enter(self, *args):
        self.refresh()

    def refresh(self):
        app = MDApp.get_running_app()
        profile = database.get_profile(app.profile_id)
        self.ids.inventory_topbar.title = tr("inventory")
        self.ids.inventory_box.clear_widgets()

        owned_ids = database.get_owned_item_ids(app.profile_id)
        catalog = content_loader.get_shop_catalog()

        for catalog_key, kind, _ in SHOP_CATEGORIES:
            all_items = catalog.get(catalog_key, [])
            owned_items = [it for it in all_items if it["price"] == 0 or it["item_id"] in owned_ids]
            if not owned_items:
                continue
            self.ids.inventory_box.add_widget(
                MDLabel(text=tr(catalog_key), font_style="Subtitle1", size_hint_y=None, height=dp(28))
            )
            self.ids.inventory_box.add_widget(self._build_grid(owned_items, kind, profile))

    def _build_grid(self, items, kind, profile):
        from kivymd.uix.gridlayout import MDGridLayout

        grid = MDGridLayout(cols=2, spacing=dp(10), size_hint_y=None, adaptive_height=True)
        for item in items:
            is_equipped = _equipped_value(profile, kind, item)
            can_unequip = is_equipped and kind == "accessory"

            card = build_item_card(
                item, kind, True, is_equipped,
                on_equip=lambda it=item, k=kind: self.equip(it, k),
                on_unequip=(lambda: self.unequip_accessory()) if can_unequip else None,
            )
            grid.add_widget(card)
        return grid

    def equip(self, item, kind):
        app = MDApp.get_running_app()
        if kind == "avatar":
            database.equip_avatar(app.profile_id, item["icon"])
        elif kind == "accessory":
            database.equip_accessory(app.profile_id, item["icon"])
        elif kind == "room":
            database.equip_room(app.profile_id, item["item_id"])
        self.refresh()

    def unequip_accessory(self):
        app = MDApp.get_running_app()
        database.unequip_accessory(app.profile_id)
        self.refresh()

    def go_back(self):
        MDApp.get_running_app().root.current = "home"


class UmBalaApp(MDApp):
    profile_id = ObjectProperty(None, allownone=True)

    def build(self):
        self.theme_cls.primary_palette = "DeepPurple"
        self.theme_cls.theme_style = "Light"
        Builder.load_string(KV)
        sm = ScreenManager(transition=SlideTransition())
        sm.add_widget(WelcomeScreen())
        sm.add_widget(HomeScreen())
        sm.add_widget(TopicListScreen())
        sm.add_widget(LessonScreen())
        sm.add_widget(ProfileScreen())
        sm.add_widget(ShopScreen())
        sm.add_widget(InventoryScreen())

        profiles = database.list_profiles()
        if profiles:
            self.profile_id = profiles[0]["id"]
            sm.current = "home"
        else:
            sm.current = "welcome"
        return sm

    def go_home(self):
        self.root.current = "home"

    def open_topics(self, subject, grade):
        screen = self.root.get_screen("topics")
        screen.open_for(subject, grade)
        self.root.current = "topics"

    def open_lesson(self, subject, grade, topic_id):
        screen = self.root.get_screen("lesson")
        screen.open_for(subject, grade, topic_id)
        self.root.current = "lesson"

    def open_inventory(self):
        self.root.current = "inventory"

    def open_shop(self):
        self.root.current = "shop"


if __name__ == "__main__":
    UmBalaApp().run()
