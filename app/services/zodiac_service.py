def zodiac_compatibility(boy_zodiac: str, girl_zodiac: str) -> dict:
    """
    MVP: soddalashtirilgan moslik.
    Keyin real jadval qo‘shamiz.
    """
    b = (boy_zodiac or "").strip().lower()
    g = (girl_zodiac or "").strip().lower()

    if not b or not g:
        return {"score": None, "text": "Burjlar kiritilmagan."}

    # juda soddalashtirilgan mapping (MVP)
    if b == g:
        return {"score": 90, "text": "Burj bir xil — bir-biringizni tez tushunishingiz mumkin. Ammo xarakter ham muhim."}

    # umumiy “o‘rtacha”
    return {"score": 70, "text": "Moslik o‘rtacha-yaxshi. Eng muhimi — muloqot va hurmat."}
