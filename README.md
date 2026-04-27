# FLASK TEAM PROJECT
<img width="851" height="371" alt="image" src="https://github.com/user-attachments/assets/bbbcea6e-25ff-438a-b11c-482724c028fa" />

## <img src="https://github.com/user-attachments/assets/a00f6bfc-416c-4fa2-ac6c-3c042a63c0b9" alt="logo" height="70" valign="middle" /> ConnectShop (커넥트샵)
플라스크를 활용해 구현한  **트렌디한 전자기기 쇼핑을 위한 최적의 이커머스 플랫폼** <br>

## 프로젝트 소개
**ConnectShop**은 최신 스마트폰, 태블릿, 무선이어폰 등 다양한 전자기기를 빠르고 직관적으로 탐색하고 구매할 수 있는 B2C 이커머스 웹 서비스입니다. 
사용자 중심의 UI/UX 설계와 Docker를 활용한 안정적인 컨테이너 기반 배포에 중점을 두어 개발되었습니다.
* **개발 기간:** 2026.04.03 ~ 2026.04.28 (3주)

## 기획 의도

## 같이 개발한 팀원들
*  **[이강토] (Front/Back):** 
  * **[김도철] (Front/Back):** 
  * **[박예인] (Front/Back):** 
  * **[이원호] (Front/Back):** 

<br>

## 기술 스택 (Tech Stack)

### Backend
<img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white"> <img src="https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white">

### Frontend
<img src="https://img.shields.io/badge/HTML5-E34F26?style=for-the-badge&logo=html5&logoColor=white"> <img src="https://img.shields.io/badge/CSS3-1572B6?style=for-the-badge&logo=css3&logoColor=white"> <img src="https://img.shields.io/badge/JavaScript-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black">

### Infrastructure & Tools
<img src="https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white"> <img src="https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white"> <img src="https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white">

<br>

## 목차

## Diagram

## 화면구현

## 주요 기능 (Key Features)

### 1. 사용자 경험(UX)을 극대화한 메가 메뉴 & 네비게이션
* 마우스 오버 시 하위 카테고리와 대표 상품 이미지가 노출되는 **반응형 메가 메뉴**
* 페이지 스크롤 시에도 화면 상단에 고정되어 이동 편의성을 높인 **Sticky Navigation Bar**

### 2. 비동기(Ajax) 기반의 쾌적한 쇼핑 환경
* **장바구니 수량 조절 및 실시간 금액 계산:** 페이지 새로고침 없이 Ajax 통신으로 즉시 총액이 반영되어 쾌적한 구매 경험 제공
* **애니메이션 찜목록:** 상품 찜하기/해제 시 부드러운 전환 효과(Fade-out) 적용

### 3. 직관적인 상품 정보 제공
* **정밀한 별점 UI:** 실제 평균 평점 데이터를 기반으로 소수점 단위까지 정확하게 시각화되는 반응형 별점 시스템 적용 (`width: {{ (product.avg_rating / 5 * 100) }}%`)
* **품절 상품 직관성 강화:** 재고가 없는 상품은 흑백 이미지와 'SOLD OUT' 오버레이로 즉시 인지 가능하도록 처리

<br>

## 🎥 서비스 화면 (Demo)
| 메가 메뉴 및 검색 | 장바구니 비동기 처리 |
| :---: | :---: |
|  |  |
| 카테고리 이동 및 직관적 검색 결과 | 새로고침 없는 실시간 수량/금액 변경 |

<br>

## 프로젝트 보고서

## 🚀 트러블 슈팅 (Trouble Shooting)

### 1. 프론트엔드: 스크롤바 제어와 Sticky Position 충돌 이슈
* **문제:** 가로 스크롤바를 숨기기 위해 `body`에 `overflow-x: hidden;`을 적용하자, 구매하기 네비게이션 바의 `position: sticky;` 기능이 무효화되는 현상 발생 (부모 요소의 overflow 속성이 hidden일 때 sticky가 해제되는 CSS 특성).
* **해결:** `hidden` 대신 최신 CSS 속성인 `overflow-x: clip;`을 적용하여, 가로 스크롤 잘림 효과는 유지하면서 스크롤 컨텍스트를 분리하지 않아 Sticky 네비게이션 기능 성공.

### 2. 인프라 배포: Docker 이미지 캐싱 및 DB 데이터 비동기화 이슈
* **문제:** 코드 수정(별점 렌더링 방식, 이미지 경로 등) 후 컨테이너를 재배포했음에도 불구하고, 도커 빌드 캐시와 구버전 DB Seed 데이터로 인해 변경 사항이 뷰에 반영되지 않는 현상.
* **해결:** 1. `seed.py` 스크립트를 재실행하여 데이터베이스 내의 이미지 경로 등 기초 데이터를 최신화.
  2. `docker build --no-cache` 옵션을 사용하여 이전 캐시를 무시하고 강제로 최신 코드가 반영된 이미지를 빌드.
  3. 로컬 테스트 검증 완료 후 Docker Hub (`docker push`)에 버전을 명시하여 안정적으로 최종 이미지 배포 완료.

<br>

## 추후 추가하고싶은 기능

## 회고

## 📄 기타 산출물
* [요구사항 정의서 (링크)](#)
* [ERD 및 아키텍처 다이어그램 (링크)](#)
* [프로젝트 발표 자료 (PDF)](#)
