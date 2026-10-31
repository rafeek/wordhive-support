#!/usr/bin/env python3
"""Emit every page of the support site, in English and in each language the app is in.

The how-to-play pages are read from HelpContent in the app's SettingsView.swift and
translated with the app's own Localizable.xcstrings, so the site says exactly what the
app's guide says, in every language. The support and privacy pages are written out in
TEXT below, and the menu paths they name (Settings → Reset all progress) are looked up in
the same catalog, so they read as they do in the app.

Run from the repo root: python3 gen_site.py [WORDSEARCH_REPO]  (default ../WordSearch)
"""
import html
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
APP = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "WordSearch")
SWIFT = open(os.path.join(APP, "WordHive", "SettingsView.swift")).read()
CATALOG = json.load(open(os.path.join(APP, "WordHive", "Localizable.xcstrings")))["strings"]

SITE = "https://rafeek.github.io/wordhive-support/"
EMAIL = "wordhivepuzzlesapp+support@gmail.com"
APPLE_PRIVACY = "https://www.apple.com/legal/privacy/"

# (code, name in its own language, folder)
LANGS = [("en", "English", ""), ("fr", "Français", "fr/"), ("es", "Español", "es/"),
         ("zh-Hans", "简体中文", "zh-Hans/")]


def app(key, lang):
    """The app's own text for an English key, in lang."""
    if lang == "en":
        return key
    entry = CATALOG.get(key)
    if entry is None:
        sys.exit(f"not in the app's catalog: {key!r}")
    if entry.get("shouldTranslate") is False:
        return key
    try:
        return entry["localizations"][lang]["stringUnit"]["value"]
    except KeyError:
        sys.exit(f"no {lang} translation in the app for: {key!r}")


# ---------------------------------------------------------------- the app's guide

OS = {"ios": "iOS", "mac": "macOS", "tv": "tvOS"}
STR = r'"((?:[^"\\]|\\.)*)"'
TOKEN = re.compile(rf'section\({STR}\)|row\({STR},\s*{STR},\s*{STR}\)|shortcut\({STR},\s*{STR}\)')


def holds(cond, plat):
    m = re.fullmatch(r"(!?)os\((\w+)\)", cond.strip())
    if not m:
        sys.exit(f"HelpContent: can't read #if {cond}")
    return (m[2] == OS[plat]) != bool(m[1])


def unquote(s):
    if "\\(" in s:
        sys.exit(f"HelpContent: interpolated text can't be looked up: {s!r}")
    return s.replace('\\"', '"').replace("\\\\", "\\")


def guide(plat):
    """HelpContent as one platform compiles it: [(section title, [(kind, a, b)])]."""
    body = SWIFT[SWIFT.index("struct HelpContent"):]
    body = body[:body.index("private static let versionString")]
    kept, stack = [], []   # stack of [a branch was taken, this branch is live]
    for line in body.split("\n"):
        s = line.strip()
        if s.startswith("#if "):
            c = holds(s[4:], plat)
            stack.append([c, c])
        elif s.startswith("#elseif "):
            top = stack[-1]
            top[1] = not top[0] and holds(s[8:], plat)
            top[0] = top[0] or top[1]
        elif s == "#else":
            top = stack[-1]
            top[1], top[0] = not top[0], True
        elif s == "#endif":
            stack.pop()
        elif all(live for _, live in stack):
            kept.append(line)
    sections = []
    for m in TOKEN.finditer("\n".join(kept)):
        if m[1] is not None:
            sections.append((unquote(m[1]), []))
        elif m[2] is not None:
            sections[-1][1].append(("row", unquote(m[3]), unquote(m[4])))
        else:
            sections[-1][1].append(("key", unquote(m[5]), unquote(m[6])))
    return sections


# name_in: Spanish takes the article in running text ("en el Mac"), not in a menu.
PLATFORMS = {
    "ios": dict(file="play-iphone-ipad.html", icon="📱", path=["Settings", "How to Play"], keys="",
                name={"en": "iPhone & iPad", "fr": "iPhone et iPad", "es": "iPhone y iPad",
                      "zh-Hans": "iPhone 与 iPad"}, name_in="el iPhone y el iPad"),
    "mac": dict(file="play-mac.html", icon="💻", path=["Help", "WordHive Help"], keys=" (⌘?)",
                name={"en": "Mac", "fr": "Mac", "es": "Mac", "zh-Hans": "Mac"}, name_in="el Mac"),
    "tv": dict(file="play-apple-tv.html", icon="📺", path=["Settings", "How to Play"], keys="",
               name={"en": "Apple TV", "fr": "Apple TV", "es": "Apple TV", "zh-Hans": "Apple TV"},
               name_in="el Apple TV"),
}


def menu_path(keys, lang, suffix=""):
    s = " → ".join(app(k, lang) for k in keys)
    if lang == "zh-Hans":   # Chinese quotes a UI name, and takes full-width brackets
        return f"“{s}”" + suffix.replace(" (", "（").replace(")", "）")
    return s + suffix


# ---------------------------------------------------------------- site text

TEXT = {
    "Support": {"fr": "Assistance", "es": "Soporte", "zh-Hans": "支持"},
    "Privacy": {"fr": "Confidentialité", "es": "Privacidad", "zh-Hans": "隐私"},
    "Language": {"fr": "Langue", "es": "Idioma", "zh-Hans": "语言"},

    # how-to-play pages
    "help.title": {"en": "How to play on {name}", "fr": "Comment jouer sur {name}",
                   "es": "Cómo jugar en {name_in}", "zh-Hans": "{name} 玩法"},
    "help.description": {"en": "How to play WordHive Puzzles on {name}.",
                         "fr": "Comment jouer à WordHive Puzzles sur {name}.",
                         "es": "Cómo jugar a WordHive Puzzles en {name_in}.",
                         "zh-Hans": "WordHive Puzzles 在 {name} 上的玩法。"},
    "help.where": {"en": "The same guide is in the app under {path}",
                   "fr": "Le même guide se trouve dans l’app, sous {path}",
                   "es": "La misma guía está en la app, en {path}",
                   "zh-Hans": "App 中的{path}里也有同样的指南"},

    # support page
    "index.description": {
        "en": "Help and contact for WordHive Puzzles, a word search game for iPhone, iPad, Mac, and Apple TV.",
        "fr": "Aide et contact pour WordHive Puzzles, un jeu de mots cachés pour iPhone, iPad, Mac et Apple TV.",
        "es": "Ayuda y contacto de WordHive Puzzles, una sopa de letras para iPhone, iPad, Mac y Apple TV.",
        "zh-Hans": "WordHive Puzzles 的帮助与联系方式。WordHive Puzzles 是一款适用于 iPhone、iPad、Mac 和 Apple TV 的找词游戏。"},
    "index.subtitle": {"en": "Help and contact for WordHive Puzzles",
                       "fr": "Aide et contact pour WordHive Puzzles",
                       "es": "Ayuda y contacto de WordHive Puzzles",
                       "zh-Hans": "WordHive Puzzles 的帮助与联系方式"},
    "index.guides": {
        "en": "Controls differ by device, so each platform has its own guide: {links}. The same guide is in the app under {ios}, or {mac} on the Mac.",
        "fr": "Les commandes varient selon l’appareil, chaque plateforme a donc son propre guide : {links}. Le même guide se trouve dans l’app, sous {ios}, ou {mac} sur Mac.",
        "es": "Los controles cambian según el dispositivo, así que cada plataforma tiene su propia guía: {links}. La misma guía está en la app, en {ios}, o en {mac} en el Mac.",
        "zh-Hans": "不同设备的操作方式不同，因此每个平台都有各自的指南：{links}。App 中的{ios}里也有同样的指南，在 Mac 上则位于{mac}。"},
    "and": {"en": ", and ", "fr": " et ", "es": " y ", "zh-Hans": " 和 "},
    "comma": {"en": ", ", "fr": ", ", "es": ", ", "zh-Hans": "、"},
    "faq": {"en": "Frequently asked", "fr": "Questions fréquentes", "es": "Preguntas frecuentes",
            "zh-Hans": "常见问题"},
    "q.source": {"en": "Where do the puzzles come from?", "fr": "D’où viennent les grilles ?",
                 "es": "¿De dónde salen las sopas de letras?", "zh-Hans": "谜题从哪里来？"},
    "a.source": {
        "en": "Every puzzle is drawn from a word bank bundled with the app. Some boards are built on your device and some are pre-built and shipped with the app. Nothing is downloaded, so the app works fully offline. There are 18 themes, each drawing on several subcategories, so the same theme gives different boards over time. Under My Puzzles you can also make your own from a list of words, or import a printed word search from a photo (iPhone, iPad, and Mac).",
        "fr": "Chaque grille est tirée d’une banque de mots fournie avec l’app. Certaines grilles sont construites sur votre appareil, d’autres sont préparées à l’avance et fournies avec l’app. Rien n’est téléchargé, si bien que l’app fonctionne entièrement hors ligne. Les 18 thèmes puisent chacun dans plusieurs sous-thèmes, et un même thème donne donc des grilles différentes au fil du temps. Dans Mes grilles, vous pouvez aussi créer les vôtres à partir d’une liste de mots, ou importer une grille de mots cachés imprimée à partir d’une photo (iPhone, iPad et Mac). Les mots à trouver sont en anglais : seule l’interface est traduite.",
        "es": "Cada sopa de letras sale de un banco de palabras incluido en la app. Algunos tableros se crean en tu dispositivo y otros vienen ya hechos con la app. No se descarga nada, así que la app funciona sin conexión. Hay 18 temas, cada uno con varios subtemas, así que un mismo tema da tableros distintos con el tiempo. En Mis sopas también puedes crear las tuyas a partir de una lista de palabras, o importar una sopa de letras impresa desde una foto (iPhone, iPad y Mac). Las palabras que hay que encontrar están en inglés. Solo la interfaz está traducida.",
        "zh-Hans": "所有谜题都取自 App 自带的词库。有些网格在你的设备上生成，有些则预先制作好、随 App 附带。无需下载任何内容，App 完全可以离线使用。共有 18 个主题，每个主题包含多个子主题，因此同一主题每次都会给出不同的网格。在“我的谜题”中，你还可以用一组单词制作自己的谜题，或从照片导入印刷版找词谜题（iPhone、iPad 和 Mac）。要找的单词是英文，只有界面经过翻译。"},
    "q.sync": {"en": "Does my game carry over between devices?",
               "fr": "Ma partie me suit-elle d’un appareil à l’autre ?",
               "es": "¿Mi partida pasa de un dispositivo a otro?",
               "zh-Hans": "游戏进度能在设备之间同步吗？"},
    "a.sync": {
        "en": "Yes, when each device is signed in to the same Apple Account with iCloud on. Your games in progress, finished puzzles, and My Puzzles are saved as you play and synced when the app comes to the foreground. A device that is offline catches up the next time it connects. Photos of imported puzzles stay on the device that read them.",
        "fr": "Oui, si chaque appareil est connecté au même compte Apple avec iCloud activé. Vos parties en cours, vos grilles terminées et Mes grilles sont enregistrées au fil du jeu et synchronisées quand l’app revient au premier plan. Un appareil hors ligne se met à jour à sa prochaine connexion. Les photos des grilles importées restent sur l’appareil qui les a lues.",
        "es": "Sí, si todos los dispositivos tienen la sesión iniciada con la misma cuenta de Apple y iCloud activado. Tus partidas en curso, las sopas terminadas y Mis sopas se guardan mientras juegas y se sincronizan cuando la app pasa a primer plano. Un dispositivo sin conexión se pone al día la próxima vez que se conecta. Las fotos de las sopas importadas se quedan en el dispositivo que las leyó.",
        "zh-Hans": "可以，只要每台设备都登录同一个 Apple 账户并打开了 iCloud。进行中的游戏、已完成的谜题和“我的谜题”会在你玩的同时保存，并在 App 回到前台时同步。离线的设备会在下次联网时跟上进度。导入谜题的照片只保留在读取它们的设备上。"},
    "q.nosync": {"en": "My game did not sync.", "fr": "Ma partie ne s’est pas synchronisée.",
                 "es": "Mi partida no se sincronizó.", "zh-Hans": "游戏没有同步。"},
    "a.nosync": {
        "en": "Check that all devices use the same Apple Account and that iCloud is on for the app. Bring the app to the foreground on the device that last played, wait a moment, then open it on the other device. Very recent moves can take a minute to arrive.",
        "fr": "Vérifiez que tous les appareils utilisent le même compte Apple et qu’iCloud est activé pour l’app. Ramenez l’app au premier plan sur l’appareil utilisé en dernier, patientez un instant, puis ouvrez-la sur l’autre appareil. Les trouvailles toutes récentes peuvent mettre une minute à arriver.",
        "es": "Comprueba que todos los dispositivos usan la misma cuenta de Apple y que iCloud está activado para la app. Pon la app en primer plano en el dispositivo donde jugaste por última vez, espera un momento y ábrela en el otro. Las últimas palabras encontradas pueden tardar un minuto en llegar.",
        "zh-Hans": "请确认所有设备使用同一个 Apple 账户，并已为本 App 打开 iCloud。在最后玩过的设备上把 App 切换到前台，稍等片刻，再在另一台设备上打开。刚刚找到的单词可能需要一分钟左右才能同步过来。"},
    "q.mp": {"en": "Multiplayer can't find a game.", "fr": "Le multijoueur ne trouve aucune partie.",
             "es": "El modo multijugador no encuentra ninguna partida.",
             "zh-Hans": "多人游戏找不到可加入的游戏。"},
    "a.mp": {
        "en": "Everyone needs to be on the same Wi-Fi network, or close by, and WordHive Puzzles needs Local Network access. Turn it on in Settings → Privacy & Security → Local Network on iPhone and iPad, or in System Settings → Privacy & Security → Local Network on a Mac. Games can be joined until the host presses Start.",
        "fr": "Tout le monde doit être sur le même réseau Wi-Fi, ou à proximité, et WordHive Puzzles doit avoir accès au réseau local. Activez-le dans Réglages → Confidentialité et sécurité → Réseau local sur iPhone et iPad, ou dans Réglages Système → Confidentialité et sécurité → Réseau local sur Mac. On peut rejoindre une partie jusqu’à ce que l’hôte appuie sur Démarrer.",
        "es": "Todos tienen que estar en la misma red Wi-Fi, o cerca, y WordHive Puzzles necesita acceso a la red local. Actívalo en Ajustes → Privacidad y seguridad → Red local en el iPhone y el iPad, o en Ajustes del Sistema → Privacidad y seguridad → Red local en el Mac. Puedes unirte a una partida hasta que el anfitrión pulse Empezar.",
        "zh-Hans": "所有人都需要连接同一个 Wi-Fi 网络或在附近，并且 WordHive Puzzles 需要本地网络访问权限。在 iPhone 和 iPad 上，可在“设置 → 隐私与安全性 → 本地网络”中将其打开。在 Mac 上，则在“系统设置 → 隐私与安全性 → 本地网络”中打开。在主持人按下“开始”之前都可以加入游戏。"},
    "requirements": {"en": "Requirements", "fr": "Configuration requise", "es": "Requisitos",
                     "zh-Hans": "系统要求"},
    "or later": {"en": "{os} or later", "fr": "{os} ou version ultérieure", "es": "{os} o posterior",
                 "zh-Hans": "{os} 或更高版本"},
    "contact": {"en": "Contact", "fr": "Contact", "es": "Contacto", "zh-Hans": "联系方式"},
    "contact.help": {"en": "If you need help with WordHive Puzzles, email me at {email}. Please include:",
                     "fr": "Si vous avez besoin d’aide avec WordHive Puzzles, écrivez-moi à {email}. Merci d’indiquer :",
                     "es": "Si necesitas ayuda con WordHive Puzzles, escríbeme a {email} e incluye lo siguiente:",
                     "zh-Hans": "如果你在使用 WordHive Puzzles 时需要帮助，请发邮件至 {email}，并附上："},
    "contact.device": {"en": "the device and its OS version", "fr": "l’appareil et la version de son système",
                       "es": "el dispositivo y la versión de su sistema", "zh-Hans": "设备及其系统版本"},
    "contact.version": {"en": "the app version, shown at the bottom of {path}",
                        "fr": "la version de l’app, indiquée en bas de {path}",
                        "es": "la versión de la app, que aparece al final de {path}",
                        "zh-Hans": "App 版本号（显示在{path}的底部）"},
    "contact.what": {"en": "what happened and what you expected instead",
                     "fr": "ce qui s’est passé et ce que vous attendiez à la place",
                     "es": "qué pasó y qué esperabas que pasara",
                     "zh-Hans": "发生了什么，以及你原本预期的结果"},

    # privacy page
    "privacy.title": {"en": "Privacy policy", "fr": "Politique de confidentialité",
                      "es": "Política de privacidad", "zh-Hans": "隐私政策"},
    "privacy.description": {
        "en": "WordHive Puzzles privacy policy. WordHive Puzzles collects no personal data and sends nothing to the developer or to any server.",
        "fr": "Politique de confidentialité de WordHive Puzzles. WordHive Puzzles ne recueille aucune donnée personnelle et n’envoie rien au développeur ni à aucun serveur.",
        "es": "Política de privacidad de WordHive Puzzles. WordHive Puzzles no recopila datos personales y no envía nada al desarrollador ni a ningún servidor.",
        "zh-Hans": "WordHive Puzzles 隐私政策。WordHive Puzzles 不收集任何个人数据，也不会向开发者或任何服务器发送任何内容。"},
    "privacy.updated": {"en": "Last updated 14 October 2026", "fr": "Dernière mise à jour : 14 octobre 2026",
                        "es": "Última actualización: 14 de octubre de 2026",
                        "zh-Hans": "最后更新：2026 年 10 月 14 日"},
    "privacy.lede": {
        "en": "WordHive Puzzles does not collect or sell any personal information, and sends nothing to me or to any server. There are no accounts, no advertising, no analytics services, and no third-party SDKs.",
        "fr": "WordHive Puzzles ne recueille ni ne vend aucune information personnelle, et n’envoie rien, ni à moi ni à aucun serveur. Il n’y a ni compte, ni publicité, ni service d’analyse, ni SDK tiers.",
        "es": "WordHive Puzzles no recopila ni vende información personal, y no envía nada ni a mí ni a ningún servidor. No hay cuentas, ni publicidad, ni servicios de análisis, ni SDK de terceros.",
        "zh-Hans": "WordHive Puzzles 不收集也不出售任何个人信息，也不会向我或任何服务器发送任何内容。没有账户、没有广告、没有分析服务，也没有第三方 SDK。"},
    "privacy.stores": {"en": "What the app stores", "fr": "Ce que l’app enregistre", "es": "Qué guarda la app",
                       "zh-Hans": "App 存储的内容"},
    "privacy.control": {"en": "Everything WordHive Puzzles saves stays under your control:",
                        "fr": "Tout ce que WordHive Puzzles enregistre reste sous votre contrôle :",
                        "es": "Todo lo que guarda WordHive Puzzles queda bajo tu control:",
                        "zh-Hans": "WordHive Puzzles 保存的一切都由你掌控："},
    "privacy.settings": {
        "en": "<strong>Your settings</strong> — accent colours, appearance, sound and voice preferences, and your multiplayer name — are stored locally on the device.",
        "fr": "<strong>Vos réglages</strong> — couleurs d’accentuation, apparence, préférences de son et de voix, et votre nom en multijoueur — sont stockés localement sur l’appareil.",
        "es": "<strong>Tus ajustes</strong> —colores de acento, apariencia, preferencias de sonido y voz, y tu nombre en el modo multijugador— se guardan localmente en el dispositivo.",
        "zh-Hans": "<strong>你的设置</strong>（强调色、外观、声音与语音偏好，以及你的多人游戏名称）仅存储在本机上。"},
    "privacy.puzzles": {
        "en": "<strong>Your puzzles</strong> — games in progress, finished puzzles, the puzzles you create or import (their letters, words, and titles), and the word list you are building in Create — are stored on the device and, when you are signed in to iCloud, in your own private iCloud key-value storage so they can continue on your other devices. This data lives in your Apple Account. I have no access to it, and Apple's {policy} governs it.",
        "fr": "<strong>Vos grilles</strong> — parties en cours, grilles terminées, grilles que vous créez ou importez (leurs lettres, leurs mots et leurs titres) et la liste de mots que vous préparez dans Créer — sont stockées sur l’appareil et, si vous êtes connecté à iCloud, dans votre propre stockage clé-valeur iCloud privé, pour que vous puissiez continuer sur vos autres appareils. Ces données résident dans votre compte Apple. Je n’y ai pas accès, et elles sont régies par la {policy} d’Apple.",
        "es": "<strong>Tus sopas</strong> —partidas en curso, sopas terminadas, las sopas que creas o importas (sus letras, palabras y títulos) y la lista de palabras que preparas en Crear— se guardan en el dispositivo y, si tienes la sesión iniciada en iCloud, en tu propio almacenamiento clave-valor privado de iCloud, para que puedas seguir en tus otros dispositivos. Estos datos están en tu cuenta de Apple. Yo no tengo acceso a ellos, y se rigen por la {policy} de Apple.",
        "zh-Hans": "<strong>你的谜题</strong>（进行中的游戏、已完成的谜题、你制作或导入的谜题及其字母、单词和标题，以及你正在“创建”中编写的单词列表）存储在设备上，登录 iCloud 时还会存入你自己的私有 iCloud 键值存储，以便在你的其他设备上继续。这些数据保存在你的 Apple 账户中。我无法访问这些数据，它们受 Apple {policy}的约束。"},
    "privacy.policy": {"en": "privacy policy", "fr": "politique de confidentialité",
                       "es": "política de privacidad", "zh-Hans": "隐私政策"},
    "privacy.photos": {
        "en": "<strong>Photos of imported puzzles</strong> are kept on the device that read them, so the puzzle can be corrected later. They are never uploaded or synced, and they are deleted along with the puzzle.",
        "fr": "<strong>Les photos des grilles importées</strong> sont conservées sur l’appareil qui les a lues, pour que la grille puisse être corrigée plus tard. Elles ne sont jamais envoyées en ligne ni synchronisées, et sont supprimées avec la grille.",
        "es": "<strong>Las fotos de las sopas importadas</strong> se guardan en el dispositivo que las leyó, para poder corregir la sopa más adelante. Nunca se suben ni se sincronizan, y se eliminan junto con la sopa.",
        "zh-Hans": "<strong>导入谜题的照片</strong>保留在读取它们的设备上，以便日后修正谜题。它们绝不会被上传或同步，并会随谜题一起删除。"},
    "privacy.delete": {
        "en": "Deleting the app removes its local settings and imported photos. Saved puzzles live in iCloud, so they outlast the app. At any time, {reset} deletes your games in progress and finished puzzles, and {deleteall} deletes the puzzles you created or imported, on every device.",
        "fr": "Supprimer l’app efface ses réglages locaux et les photos importées. Les grilles enregistrées résident dans iCloud et survivent donc à l’app. À tout moment, {reset} supprime vos parties en cours et vos grilles terminées, et {deleteall} supprime les grilles que vous avez créées ou importées, sur tous les appareils.",
        "es": "Al eliminar la app se borran sus ajustes locales y las fotos importadas. Las sopas guardadas están en iCloud, así que sobreviven a la app. En cualquier momento, {reset} elimina tus partidas en curso y las sopas terminadas, y {deleteall} elimina las sopas que creaste o importaste, en todos los dispositivos.",
        "zh-Hans": "删除 App 会移除其本地设置和导入的照片。已保存的谜题存放在 iCloud 中，因此删除 App 后依然存在。你可以随时通过{reset}删除进行中的游戏和已完成的谜题，通过{deleteall}删除你制作或导入的谜题，所有设备上都会一并删除。"},
    "privacy.doesnt": {"en": "What the app does not do", "fr": "Ce que l’app ne fait pas",
                       "es": "Lo que la app no hace", "zh-Hans": "App 不会做的事"},
    "privacy.personal": {
        "en": "No personal information is collected — no name, email, contacts, or location — and photos you import never leave your device.",
        "fr": "Aucune information personnelle n’est recueillie — ni nom, ni adresse e-mail, ni contacts, ni position — et les photos que vous importez ne quittent jamais votre appareil.",
        "es": "No se recopila ninguna información personal —ni nombre, ni correo electrónico, ni contactos, ni ubicación—, y las fotos que importas nunca salen de tu dispositivo.",
        "zh-Hans": "不收集任何个人信息（姓名、电子邮件、联系人或位置都不收集），你导入的照片也绝不会离开你的设备。"},
    "privacy.tracking": {
        "en": "No identifiers are used for tracking, and no data is shared with data brokers or advertisers.",
        "fr": "Aucun identifiant n’est utilisé pour le suivi, et aucune donnée n’est partagée avec des courtiers en données ou des annonceurs.",
        "es": "No se usa ningún identificador para rastrear, y no se comparte ningún dato con intermediarios de datos ni anunciantes.",
        "zh-Hans": "不使用任何标识符进行跟踪，也不会与数据经纪商或广告商共享任何数据。"},
    "privacy.analytics": {
        "en": "No usage analytics are collected or uploaded. The app ships with analytics collection disabled at the source level.",
        "fr": "Aucune statistique d’utilisation n’est recueillie ni envoyée. L’app est distribuée avec la collecte de statistiques désactivée dans son code source.",
        "es": "No se recopilan ni se envían estadísticas de uso. La app se distribuye con la recopilación de estadísticas desactivada en su propio código.",
        "zh-Hans": "不收集也不上传任何使用情况分析数据。App 发布时已在源代码层面关闭了分析数据收集。"},
    "privacy.offline": {
        "en": "Puzzles are generated on your device or bundled with the app, so playing on your own needs no network access.",
        "fr": "Les grilles sont créées sur votre appareil ou fournies avec l’app, si bien que jouer seul ne demande aucun accès au réseau.",
        "es": "Las sopas se generan en tu dispositivo o vienen incluidas en la app, así que jugar solo no requiere conexión de red.",
        "zh-Hans": "谜题在你的设备上生成或随 App 附带，因此单人游戏无需联网。"},
    "privacy.camera": {"en": "Camera and photos", "fr": "Appareil photo et photos", "es": "Cámara y fotos",
                       "zh-Hans": "相机与照片"},
    "privacy.camera.body": {
        "en": "To import a printed word search, WordHive Puzzles uses the camera on iPhone and iPad, or the photos and image files you choose. It sees only the photos you take or pick, and reads them entirely on your device.",
        "fr": "Pour importer une grille de mots cachés imprimée, WordHive Puzzles utilise l’appareil photo sur iPhone et iPad, ou les photos et fichiers image que vous choisissez. L’app ne voit que les photos que vous prenez ou sélectionnez, et les lit entièrement sur votre appareil.",
        "es": "Para importar una sopa de letras impresa, WordHive Puzzles usa la cámara en el iPhone y el iPad, o las fotos y archivos de imagen que elijas. La app solo ve las fotos que tomas o eliges, y las lee por completo en tu dispositivo.",
        "zh-Hans": "为了导入印刷版找词谜题，WordHive Puzzles 会在 iPhone 和 iPad 上使用相机，或使用你选择的照片和图像文件。它只能看到你拍摄或选取的照片，并且完全在你的设备上读取。"},
    "privacy.mp.body": {
        "en": "Multiplayer connects directly to other devices on the same Wi-Fi network or close by, with no server in between. The app asks for Local Network access to find and join games. A game shares your player name — your device's name until you type another — along with your finds and score with the other players in it, and a host's name is visible to anyone nearby looking for games. Multiplayer games are not saved.",
        "fr": "Le multijoueur se connecte directement aux autres appareils du même réseau Wi-Fi ou à proximité, sans serveur intermédiaire. L’app demande l’accès au réseau local pour trouver et rejoindre des parties. Une partie partage avec les autres joueurs votre nom de joueur (le nom de votre appareil tant que vous n’en tapez pas un autre), vos trouvailles et votre score, et le nom d’un hôte est visible par toute personne à proximité qui cherche une partie. Les parties multijoueurs ne sont pas enregistrées.",
        "es": "El modo multijugador se conecta directamente con otros dispositivos de la misma red Wi-Fi o cercanos, sin ningún servidor de por medio. La app pide acceso a la red local para encontrar partidas y unirse a ellas. Una partida comparte con los demás jugadores tu nombre de jugador (el nombre de tu dispositivo hasta que escribas otro), las palabras que encuentras y tu puntuación, y el nombre del anfitrión es visible para cualquiera que busque partidas cerca. Las partidas multijugador no se guardan.",
        "zh-Hans": "多人游戏直接连接同一 Wi-Fi 网络中或附近的其他设备，中间不经过任何服务器。App 会请求本地网络访问权限，用于查找和加入游戏。在一局游戏中，你的玩家名称（在你输入其他名称之前为设备名称）以及你找到的单词和得分会与同局的其他玩家共享，主持人的名称对附近正在寻找游戏的任何人可见。多人游戏不会被保存。"},
    "privacy.speech": {"en": "Speech", "fr": "Synthèse vocale", "es": "Voz", "zh-Hans": "语音"},
    "privacy.speech.body": {
        "en": "Spoken celebration phrases use Apple's built-in speech synthesis with the voices installed on your device. WordHive Puzzles does not record audio and does not use the microphone. Dictating words in Create on Apple TV uses the system's own dictation.",
        "fr": "Les félicitations prononcées utilisent la synthèse vocale intégrée d’Apple, avec les voix installées sur votre appareil. WordHive Puzzles n’enregistre aucun son et n’utilise pas le micro. La dictée de mots dans Créer sur Apple TV passe par la dictée du système.",
        "es": "Las frases de celebración habladas usan la síntesis de voz integrada de Apple con las voces instaladas en tu dispositivo. WordHive Puzzles no graba audio ni usa el micrófono. Dictar palabras en Crear en el Apple TV usa el dictado del propio sistema.",
        "zh-Hans": "朗读的庆祝语使用 Apple 内置的语音合成以及你设备上安装的语音。WordHive Puzzles 不录制音频，也不使用麦克风。在 Apple TV 上的“创建”中听写单词时，使用的是系统自带的听写功能。"},
    "privacy.children": {"en": "Children", "fr": "Enfants", "es": "Niños", "zh-Hans": "儿童"},
    "privacy.children.body": {
        "en": "WordHive Puzzles is suitable for all ages and collects no data from anyone, including children under 13.",
        "fr": "WordHive Puzzles convient à tous les âges et ne recueille aucune donnée sur personne, y compris les enfants de moins de 13 ans.",
        "es": "WordHive Puzzles es apto para todas las edades y no recopila datos de nadie, incluidos los menores de 13 años.",
        "zh-Hans": "WordHive Puzzles 适合所有年龄段，不收集任何人的数据，包括 13 岁以下的儿童。"},
    "privacy.changes": {"en": "Changes", "fr": "Modifications", "es": "Cambios", "zh-Hans": "政策变更"},
    "privacy.changes.body": {
        "en": "If a future version of WordHive Puzzles collects anything, I will update this policy before that version is released, and the date at the top will change.",
        "fr": "Si une version future de WordHive Puzzles recueille quoi que ce soit, je mettrai à jour cette politique avant sa sortie, et la date en haut de la page changera.",
        "es": "Si una versión futura de WordHive Puzzles recopila algo, actualizaré esta política antes de publicarla, y la fecha de arriba cambiará.",
        "zh-Hans": "如果 WordHive Puzzles 的未来版本会收集任何信息，我会在该版本发布前更新本政策，页面顶部的日期也会随之更改。"},
    "privacy.contact": {"en": "If you have questions about this policy, email me at {email}.",
                        "fr": "Pour toute question sur cette politique, écrivez-moi à {email}.",
                        "es": "Si tienes preguntas sobre esta política, escríbeme a {email}.",
                        "zh-Hans": "如果你对本政策有任何疑问，请发邮件至 {email}。"},
}


def t(key, lang, **kw):
    entry = TEXT[key]
    s = entry.get(lang) or (key if lang == "en" else None)
    if s is None:
        sys.exit(f"no {lang} text for {key!r}")
    return s.format(**kw) if kw else s


# ---------------------------------------------------------------- page shell

NAV = ["index.html", "play-iphone-ipad.html", "play-mac.html", "play-apple-tv.html", "privacy.html"]

# The English support page sends a first visit on to the reader's language. Choosing a
# language in the footer is remembered, so it never overrides that choice.
REDIRECT = """<script>
try {
  if (!localStorage.getItem("lang")) {
    for (const l of navigator.languages || [navigator.language]) {
      const s = l.toLowerCase()
      const m = s.startsWith("en") ? "en" : s.startsWith("fr") ? "fr" : s.startsWith("es") ? "es"
        : s.startsWith("zh") && !/hant|tw|hk|mo/.test(s) ? "zh-Hans" : null
      if (m) { if (m !== "en") location.replace(m + "/"); break }
    }
  }
} catch (e) {}
</script>
"""


def nav_label(href, lang):
    if href == "index.html":
        return t("Support", lang)
    if href == "privacy.html":
        return t("Privacy", lang)
    return next(p for p in PLATFORMS.values() if p["file"] == href)["name"][lang]


def shell(lang, folder, file, title, description, icon, h1, subtitle, body, help_page=False):
    up = "../" if folder else ""
    links = "\n".join(
        f'    <a href="{href}"{" aria-current=\"page\"" if href == file else ""}>{html.escape(nav_label(href, lang))}</a>'
        for href in NAV)
    langs = " · ".join(
        f'<a href="{up}{d}{file}" hreflang="{c}" lang="{c}"{" aria-current=\"true\"" if c == lang else ""}'
        f""" onclick="try {{ localStorage.setItem('lang', '{c}') }} catch (e) {{}}">{n}</a>"""
        for c, n, d in LANGS)
    alternates = "\n".join(f'<link rel="alternate" hreflang="{c}" href="{SITE}{d}{file}">' for c, _, d in LANGS)
    redirect = REDIRECT if lang == "en" and file == "index.html" else ""
    return f'''<!DOCTYPE html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>WordHive Puzzles — {html.escape(title)}</title>
<meta name="description" content="{html.escape(description)}">
{alternates}
<link rel="alternate" hreflang="x-default" href="{SITE}{file}">
<link rel="icon" href="{up}icon.png">
<link rel="stylesheet" href="{up}style.css">
{redirect}</head>
<body>
<main{' class="help"' if help_page else ""}>

<header class="site">
  <a class="brand" href="index.html"><img class="mark" src="{up}icon.png" alt="" width="32" height="32">WordHive Puzzles</a>
  <nav>
{links}
  </nav>
  <script>document.querySelector('.site nav [aria-current]').scrollIntoView({{inline: "center", block: "nearest"}})</script>
</header>

<div class="title">
  <div class="mark" aria-hidden="true">{icon}</div>
  <div>
    <h1>{h1}</h1>
    <p>{subtitle}</p>
  </div>
</div>

{body}

<hr>
<footer>
  <nav class="langs" aria-label="{html.escape(t("Language", lang))}">{langs}</nav>
  <p>© 2026 Rafeek Rahamut</p>
</footer>

</main>
</body>
</html>
'''


# ---------------------------------------------------------------- pages

def help_page(lang, folder, plat):
    p = PLATFORMS[plat]
    name = p["name"][lang]
    names = dict(name=name, name_in=p.get("name_in", name))
    out = []
    for title, rows in guide(plat):
        heading = app(title, lang)
        cells = []
        for kind, a, b in rows:
            a, b = html.escape(app(a, lang)), html.escape(app(b, lang))
            cells.append(f'<div class="row"><strong>{a}</strong><p>{b}</p></div>' if kind == "row"
                         else f'<div class="row keys"><span>{a}</span><kbd>{b}</kbd></div>')
        out.append(f"<h2>{html.escape(heading.capitalize())}</h2>\n<div class=\"card\">\n" + "\n".join(cells) + "\n</div>")
    where = html.escape(menu_path(p["path"], lang, p["keys"]))
    return shell(lang, folder, p["file"], t("help.title", lang, **names),
                 t("help.description", lang, **names), p["icon"],
                 html.escape(t("help.title", lang, **names)), t("help.where", lang, path=where),
                 "\n\n".join(out), help_page=True)


def mailto():
    return f'<a href="mailto:{EMAIL}">{EMAIL}</a>'


def index_page(lang, folder):
    guides = [f'<a href="{p["file"]}">{html.escape(p["name"][lang])}</a>' for p in PLATFORMS.values()]
    links = t("comma", lang).join(guides[:-1]) + t("and", lang) + guides[-1]
    ios = html.escape(menu_path(["Settings", "How to Play"], lang))
    mac = html.escape(menu_path(["Help", "WordHive Help"], lang, " (⌘?)"))
    faq = "\n\n".join(f"<h3>{t('q.' + k, lang)}</h3>\n<p>{t('a.' + k, lang)}</p>"
                      for k in ["source", "sync", "nosync", "mp"])
    req = "\n".join(f"  <li>{html.escape(PLATFORMS[p]['name'][lang])} — {t('or later', lang, os=o)}</li>"
                    for p, o in [("ios", "iOS / iPadOS 17"), ("mac", "macOS 14"), ("tv", "tvOS 17")])
    version = html.escape(menu_path(["Settings", "How to Play"], lang))
    body = f"""<h2>{html.escape(app("How to play", lang))}</h2>
<p>{t("index.guides", lang, links=links, ios=ios, mac=mac)}</p>

<h2>{t("faq", lang)}</h2>
<div class="faq">

{faq}

</div>

<h2>{t("requirements", lang)}</h2>
<ul>
{req}
</ul>

<h2>{t("contact", lang)}</h2>
<p>{t("contact.help", lang, email=mailto())}</p>
<ul>
  <li>{t("contact.device", lang)}</li>
  <li>{t("contact.version", lang, path=version)}</li>
  <li>{t("contact.what", lang)}</li>
</ul>"""
    return shell(lang, folder, "index.html", t("Support", lang), t("index.description", lang), "🛟",
                 t("Support", lang), t("index.subtitle", lang), body)


def privacy_page(lang, folder):
    policy = f'<a href="{APPLE_PRIVACY}">{t("privacy.policy", lang)}</a>'
    reset = html.escape(menu_path(["Settings", "Reset all progress"], lang))
    deleteall = html.escape(menu_path(["Settings", "Delete all My Puzzles"], lang))
    if lang == "zh-Hans":   # the label quotes My Puzzles itself, so nest it
        deleteall = deleteall.replace("“我的谜题”", "‘我的谜题’")
    def li(*keys):
        return "\n".join(f"  <li>{t(k, lang, policy=policy)}</li>" for k in keys)
    mp = app("MULTIPLAYER", lang).capitalize()
    body = f"""<p class="lede">{t("privacy.lede", lang)}</p>

<h2>{t("privacy.stores", lang)}</h2>
<p>{t("privacy.control", lang)}</p>
<ul>
{li("privacy.settings", "privacy.puzzles", "privacy.photos")}
</ul>
<p>{t("privacy.delete", lang, reset=reset, deleteall=deleteall)}</p>

<h2>{t("privacy.doesnt", lang)}</h2>
<ul>
{li("privacy.personal", "privacy.tracking", "privacy.analytics", "privacy.offline")}
</ul>

<h2>{t("privacy.camera", lang)}</h2>
<p>{t("privacy.camera.body", lang)}</p>

<h2>{html.escape(mp)}</h2>
<p>{t("privacy.mp.body", lang)}</p>

<h2>{t("privacy.speech", lang)}</h2>
<p>{t("privacy.speech.body", lang)}</p>

<h2>{t("privacy.children", lang)}</h2>
<p>{t("privacy.children.body", lang)}</p>

<h2>{t("privacy.changes", lang)}</h2>
<p>{t("privacy.changes.body", lang)}</p>

<h2>{t("contact", lang)}</h2>
<p>{t("privacy.contact", lang, email=mailto())}</p>"""
    return shell(lang, folder, "privacy.html", t("privacy.title", lang), t("privacy.description", lang), "🔒",
                 t("privacy.title", lang), t("privacy.updated", lang), body)


for lang, _, folder in LANGS:
    if folder:
        os.makedirs(os.path.join(HERE, folder), exist_ok=True)
    pages = {"index.html": index_page(lang, folder), "privacy.html": privacy_page(lang, folder)}
    for plat, p in PLATFORMS.items():
        pages[p["file"]] = help_page(lang, folder, plat)
    for file, text in pages.items():
        with open(os.path.join(HERE, folder, file), "w") as f:
            f.write(text)
        print("wrote", folder + file)
