
from src.calculators.bazi import BaziCalculator
b = BaziCalculator().calculate_bazi(1979, 10, 23, 4, 0, '女') # 4am
print(f'Year: {b['四柱']['年柱']['天干']}{b['四柱']['年柱']['地支']}')
print(f'Month: {b['四柱']['月柱']['天干']}{b['四柱']['月柱']['地支']}')
print(f'Day: {b['四柱']['日柱']['天干']}{b['四柱']['日柱']['地支']}')
print(f'Hour: {b['四柱']['時柱']['天干']}{b['四柱']['時柱']['地支']}')

# Check 2026 (Bing Wu) relation
print(f'2026: Bing Wu')

