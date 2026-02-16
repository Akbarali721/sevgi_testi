from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional


# =========================
# 1) Natija strukturalari
# =========================

@dataclass(frozen=True)
class ResultBlock:
    title: str
    text: str
    bullets: List[str]


@dataclass(frozen=True)
class ResultProfile:
    block1: ResultBlock  # Romantik kayfiyat + muloyim xulosa
    block2: ResultBlock  # Ishonch + nazorat + amaliy qadamlar


# =========================
# 2) Kontent (mapping)
# =========================
# Kalit: (boy_zodiac, girl_zodiac)  -> qiymat: 2 ta blok
# Zodiac nomlarini loyihangda qaysi formatda ishlatayotgan bo‘lsang, shunga mos yoz.
# Masalan: "Aries", "Taurus"... yoki "Qo'y", "Buzoq"...
PROFILES: Dict[Tuple[str, str], ResultProfile] = {}


def _make_profile(
    b1_title: str,
    b1_text: str,
    b1_bullets: List[str],
    b2_title: str,
    b2_text: str,
    b2_bullets: List[str],
) -> ResultProfile:
    return ResultProfile(
        block1=ResultBlock(title=b1_title, text=b1_text, bullets=b1_bullets),
        block2=ResultBlock(title=b2_title, text=b2_text, bullets=b2_bullets),
    )


# ===== Default (fallback) profil =====
DEFAULT_PROFILE: ResultProfile = _make_profile(
    b1_title="Muloyim xulosa",
    b1_text=(
        "Sizning munosabatda iliq energiya bor. Ba’zan ayol kishi o‘zi ham nimani xohlashini aniq "
        "aytmaydi — lekin u erkakdan vaziyatni “tutib turish”ni, ya’ni ishonchli qaror kutishi mumkin."
    ),
    b1_bullets=[
        "U sizdan mayda e’tibor va g‘amxo‘rlikni ko‘proq sezadi.",
        "Sizning kuchli tomoningiz — tashabbus va mas’uliyatni olish.",
        "Romantika ko‘pincha katta sovg‘a emas, kichik harakatlardan boshlanadi.",
    ],
    b2_title="Siz uchun aniq yo‘l-yo‘riq",
    b2_text=(
        "Sizga kerak bo‘ladigan narsa — “to‘g‘ri qildimmi?” degan ishonch. Bu yerda siz vaziyatni "
        "kontrol qilasiz: gapni ham, kayfiyatni ham muloyim ushlab turasiz."
    ),
    b2_bullets=[
        "Bugun: 1 ta qisqa, samimiy xabar yuboring (uzun izohsiz).",
        "Ertaga: kichkina surpriz qiling — shaxsiy bo‘lsin (u yoqtiradigan narsa).",
        "Savolni ko‘paytirmang: “Nima xohlaysan?” o‘rniga o‘zingiz yumshoq taklif bering.",
        "Oxirida: ‘Seni xursand qilish menga yoqadi’ degan bitta jumla bilan yopib qo‘ying.",
    ],
)


# ===== Namuna profillar (xohlasang ko‘paytirasan) =====
# Pastdagilar shunchaki misol. O‘zingning kontenting bilan almashtirasan.

PROFILES[("Aries", "Libra")] = _make_profile(
    b1_title="Muloyim xulosa",
    b1_text=(
        "Sizda romantik tashabbus kuchli. U esa ko‘proq muloyim e’tibor va ishonchli qadam kutadi. "
        "Gapning ko‘p bo‘lishi shart emas — tuyg‘u sezilishi muhim."
    ),
    b1_bullets=[
        "U sizdan ‘meni eslayapsan’ degan signallarni kutadi.",
        "Sizning rolingiz — kayfiyatni ko‘tarib turish.",
    ],
    b2_title="Siz uchun aniq yo‘l-yo‘riq",
    b2_text=(
        "U ba’zan o‘zi ham xohishini aniq aytmaydi, lekin sizdan qaror kutadi. "
        "Qarorni siz qilganingizda u o‘zini xavfsiz his qiladi."
    ),
    b2_bullets=[
        "1 qadam: ‘Bugun kechqurun kichkina rejam bor’ deb oldindan iliq signal bering.",
        "2 qadam: sovg‘a shart emas — e’tibor shart (kichkina shirinlik ham bo‘ladi).",
        "3 qadam: ‘Men seni tushunishga harakat qilyapman’ degan jumla ishlaydi.",
    ],
)

PROFILES[("Cancer", "Pisces")] = _make_profile(
    b1_title="Muloyim xulosa",
    b1_text=(
        "Sizlarda hissiyot chuqur. Bu yaxshi — faqat romantikani oddiy, tabiiy qilib berish kerak. "
        "U ko‘proq samimiyatni, siz esa aniq yo‘lni xohlaysiz."
    ),
    b1_bullets=[
        "Muloyim gaplar sizlarda kuchli ishlaydi.",
        "E’tibor — eng katta sovg‘a.",
    ],
    b2_title="Siz uchun aniq yo‘l-yo‘riq",
    b2_text=(
        "Siz vaziyatni ‘muloyim liderlik’ bilan boshqarsangiz, u yanada ochiladi. "
        "Gapning toni yumshoq, qaror esa aniq bo‘lsin."
    ),
    b2_bullets=[
        "Bugun: bitta iliq kompliment (tashqi emas, xarakteriga).",
        "Keyin: 10 daqiqalik birga vaqt — telefonlarsiz.",
        "Oxiri: ‘Seni xursand ko‘rsam men ham xursand bo‘laman’ deb yakunlang.",
    ],
)


# =========================
# 3) Helper funksiyalar
# =========================

def normalize_key(value: str) -> str:
    """
    Zodiac nomlari turlicha yozilishi mumkin: ' aries ', 'ARIES'...
    Shu funksiyada formatlaymiz.
    """
    if value is None:
        return ""
    return value.strip()


def get_profile(boy_zodiac: str, girl_zodiac: str) -> ResultProfile:
    """
    Asosiy funksiya:
    - (boy, girl) juftlik bo‘yicha profil qidiradi
    - topilmasa fallback qaytaradi
    """
    k1 = normalize_key(boy_zodiac)
    k2 = normalize_key(girl_zodiac)

    # 1) aniq juftlik
    profile = PROFILES.get((k1, k2))
    if profile:
        return profile

    # 2) teskari juftlik (ba’zan ikkala yo‘nalishda ham ishlatib yuborish mumkin)
    profile = PROFILES.get((k2, k1))
    if profile:
        return profile

    # 3) default
    return DEFAULT_PROFILE


def get_profile_dict(boy_zodiac: str, girl_zodiac: str) -> dict:
    """
    Agar sendagi code/template dict bilan ishlashni xohlasa,
    ResultProfile ni dict ko‘rinishiga o‘girib beradi.
    """
    p = get_profile(boy_zodiac, girl_zodiac)
    return {
        "block1": {"title": p.block1.title, "text": p.block1.text, "bullets": p.block1.bullets},
        "block2": {"title": p.block2.title, "text": p.block2.text, "bullets": p.block2.bullets},
    }
