WEATHER_CONDITION_FIXES = {
    '튼구름': '구름 많음',
    '튼구름 많음': '구름 많음',
    '온흐림': '흐림',
    '흐린': '흐림',
    '맑은 하늘': '맑음',
    '구름조금': '구름 조금',
    '약한 눈': '가벼운 눈',
    '약한 비': '가벼운 비',
    '얕은 비': '가벼운 비',
    '얕은 눈': '가벼운 눈',
}


def normalize_weather_condition(condition):
    text = str(condition or '').strip()
    if not text:
        return '정보 없음'
    return WEATHER_CONDITION_FIXES.get(text, text)
