from collections import Counter

def build_profile(answers: list[str]) -> dict:
    """
    answers: ['A','B','A',...]
    """

    count = Counter(answers)
    a = count.get("A", 0)
    b = count.get("B", 0)

    # Dominant ehtiyojni aniqlaymiz
    if a >= b:
        key = "emotion"
    else:
        key = "attention"

    profiles = {
        "emotion": {
            "summary": (
                "Ko‘rinishidan, u munosabatda "
                "iliq so‘zlar, samimiy e’tibor va hissiy yaqinlikni "
                "ko‘proq his qilishni xohlayotgandek."
            ),
            "bullets": [
                "💬 Ba’zan oddiy, lekin samimiy gaplar unga katta ta’sir qiladi",
                "❤️ E’tibor — sovg‘adan ko‘ra muhimroq bo‘lishi mumkin",
                "🤍 U tinglanayotganini his qilsa, yanada ochiladi"
            ],
            "tip": (
                "Kichik maslahat: unga vaqti-vaqti bilan "
                "hislaringizni ochiq aytib ko‘ring."
            )
        },
        "attention": {
            "summary": (
                "Ko‘rinishidan, u munosabatda "
                "barqarorlik, amaliy g‘amxo‘rlik va "
                "kundalik mayda e’tiborlarni ko‘proq qadrlayotgandek."
            ),
            "bullets": [
                "🌱 U uchun doimiylik va ishonch muhim",
                "🕰 Birga o‘tkazilgan vaqt — asosiy signal",
                "🤝 Amalda ko‘rsatilgan g‘amxo‘rlik unga yaqin"
            ],
            "tip": (
                "Kichik maslahat: va’dadan ko‘ra, "
                "amaldagi mayda ishlar kuchliroq bo‘lishi mumkin."
            )
        }
    }

    profile = profiles[key]

    return {
        "key": key,
        "summary": profile["summary"],
        "bullets": profile["bullets"],
        "tip": profile["tip"]
    }
