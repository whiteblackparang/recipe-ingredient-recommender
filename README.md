# Food Recipe Recommendation

보유 재료 기반 레시피 추천 서비스

## 개요

- **데이터**: Kaggle "Food Ingredients and Recipes Dataset with Images", 13,501개 레시피 + 이미지 13,582장
- **핵심 역량**: EDA, 규칙 기반 추천 로직 설계 및 반복 개선, 편향 검증, Streamlit 대시보드
- **최종 산출물**: 재료 매칭 기반 레시피 추천 웹 데모

## 프로젝트 진행 단계

### 1. 데이터 다운로드
CSV 13,501행 × 6컬럼 + 이미지 13,582장

### 2. 데이터 구조 파악 (`src/data.py`)
- 결측치: Title 5건, Instructions 8건
- Image_Name 중복 29건, 이미지 미존재(`#NAME?`) 30건
- 이미지 폴더 연결: 13,582개 파일, 매핑 누락 0건

### 3. 전처리 (`src/preprocess.py`)
- `Ingredients` 문자열 → 리스트 파싱 (`ast.literal_eval`)
- 수량/단위/유니코드 분수/괄호 설명 제거 → 핵심 재료명 추출
- 원본 13,501행 → 전처리 후 13,489행

**이슈 1**: `Cleaned_Ingredients` 컬럼명·실제 상태 불일치, 원본과 거의 동일한 미정제 상태
**이슈 2**: 1차 정규화 로직의 `teaspoon`/`tablespoon` 풀네임 누락 → `salt` 3갈래 분산 집계 → EDA 단계에서 발견, 규칙 보강

### 4. EDA (`notebooks/01_data_exploration.ipynb`)
- 레시피당 평균 재료 개수: 10.6개 (범위: 1~51개)
- 재료 2개 이하 초단순 레시피: 112건
- 고유 재료 26,818종 중 74.3%(19,923종) 1회성 등장 — 롱테일 분포
- 재료 개수-조리법 길이 상관계수: 0.524, 약한 양의 상관
- Top 재료: salt(7,480) > garlic(3,847) > sugar(3,499) > butter(3,445) > olive oil(2,764)

### 5. Feature Engineering (`src/features.py`)
- 재료별 frequency, frequency_ratio, rarity(IDF 스타일: log(1/frequency_ratio)) 산출
- common 재료(등장 빈도 5% 이상) 21개 식별
- 레시피별 ingredient_rarity_avg, common_ingredient_ratio 생성

### 6~7. 추천 로직 설계 및 구현 (`src/recommend.py`)

| 버전 | 방식 |
|---|---|
| V1 | 단순 매칭률 |
| V2 | rarity 가중 매칭 비율 - 부족 재료 비율 페널티 |
| V3 | rarity 절대량 - 부족 재료 개수 페널티 |

### 8. 추천 결과 검증 (`src/evaluate.py`)

**발견**: V2, common 재료 편향
- 전체 평균 common_ingredient_ratio: 0.287
- V2 추천 결과 평균: 0.73~1.00 (테스트 유저 5명 전원)

**개선**: 절대량 기반 V3 전환
- 편향 해소: 5명 중 3명 (0.73~0.90 → 0.46~0.47)
- 평균 재료 수: 3~5개 → 7~9개
- 잔존 2건: 유저 입력 자체가 common 재료 한정, 정상 동작으로 판단

**최종 채택: V3**

### 9. 시각화/Dashboard (`app/app.py`)
Streamlit 기반 데모, 3단 구성
- 상단: 요약 지표 4종 (추천 수/평균 부족재료/평균 rarity/평균 common 비율)
- 중단: 레시피별 점수 막대그래프
- 하단: 이미지 카드 그리드 3열 (사진/제목/가진 재료/부족 재료)

## 폴더 구조
food-recipe-recommendation/
├── README.md
├── REPORT.md
├── config.py
├── requirements.txt
├── data/
│ ├── Food_Ingredients_and_Recipe_Dataset_with_Image_Name_Mapping.csv
│ └── Food Images/
├── src/
│ ├── data.py
│ ├── preprocess.py
│ ├── features.py
│ ├── recommend.py
│ └── evaluate.py
├── notebooks/
│ └── 01_data_exploration.ipynb
├── app/
│ └── app.py
└── outputs/
├── recipes_cleaned.csv
├── recipes_with_features.csv
├── ingredient_stats.csv
└── fig_*.png


## 실행 방법
```bash
pip install -r requirements.txt

python -m src.data
python -m src.preprocess
python -m src.features
python -m src.recommend
python -m src.evaluate

streamlit run app/app.py
```

## 기술 스택
Python, Pandas, NumPy, Matplotlib, Seaborn, scikit-learn, Streamlit

## Tableau Dashboard

[Recipe Ingredient Explorer (재료 기반 레시피 인사이트)](https://public.tableau.com/app/profile/jonghun.lee4755/viz/1_17896992535150/1)

13,489개 레시피를 재료 관점에서 탐색하는 인터랙티브 대시보드.
- 고유 재료 26,818종 중 상위 20개 빈도 시각화
- 재료 개수 vs Rarity 분포 확인
- Top20 재료 클릭 시 해당 재료 포함 레시피로 필터링되는 Filter Action 구현