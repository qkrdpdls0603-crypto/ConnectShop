# FLASK TEAM PROJECT
<img width="851" height="371" alt="image" src="https://github.com/user-attachments/assets/bbbcea6e-25ff-438a-b11c-482724c028fa" />

## <img src="https://github.com/user-attachments/assets/a00f6bfc-416c-4fa2-ac6c-3c042a63c0b9" alt="logo" height="70" valign="middle" /> ConnectShop (커넥트샵)
플라스크를 활용해 구현한  **트렌디한 전자기기 쇼핑을 위한 최적의 이커머스 플랫폼** <br>

## 프로젝트 소개
**ConnectShop**은 최신 스마트폰, 태블릿, 무선이어폰 등 다양한 전자기기를 빠르고 직관적으로 탐색하고 구매할 수 있는 B2C 이커머스 웹 서비스입니다. 
사용자 중심의 UI/UX 설계와 Docker를 활용한 안정적인 컨테이너 기반 배포에 중점을 두어 개발되었습니다.
* **개발 기간: 2026.04.03 ~ 2026.04.28 (3주)**

## 기획 의도 및 프로젝트 배경
**1. 실무에 직결되는 상용 이커머스 아키텍처 경험** 
* 실제 시장에서 서비스되는 대형 전자기기 쇼핑몰의 구조와 비즈니스 로직을 철저히 벤치마킹했습니다.
* 단순한 CRUD(읽기/쓰기) 게시판 형태를 넘어, 상품 **탐색부터 장바구니, 결제, 배송 처리로 이어지는 B2C 구매의 핵심 흐름(User Flow)** 을 완벽하게 구현하는 것을 최우선 목표로 삼았습니다.
* 특히, 세션과 데이터베이스 설계를 통해 **회원과 비회원의 권한 및 이용 가능 기능을 명확히 분리함** 으로써 실무 수준의 서비스 로직 처리 능력을 길렀습니다.

**2. 학습 내용의 총체적 적용 및 풀스택(Full-Stack) 역량 증명**
* K-Digital Training 과정에서 배운 모든 이론과 기술을 파편화해 두지 않고, 하나의 완성된 프로덕트로 엮어내는 **'기술 통합의 장'** 으로 활용했습니다.
* 직관적인 UI/UX 설계부터 데이터베이스 모델링, 백엔드 로직 처리, 그리고 최종적인 배포 환경 구축에 이르기까지 **프론트엔드와 백엔드의 전체 사이클을 모두 경험하며 풀스택 개발자로서의 시야**를 넓히고자 했습니다. <br>

**3. 체계적인 분업과 시너지를 위한 최적의 팀 협업 모델**
* 이커머스 플랫폼은 유저 관리, 상품 전시, 리뷰, 장바구니 등 기능적 도메인이 명확하게 나뉘어 있어 **팀원 간의 효율적인 역할 분담과 깃허브(GitHub) 협업을 연습하기에 가장 적합한 주제**입니다.
* 각자가 맡은 모듈을 독립적으로 개발하고 이를 하나의 서비스로 안전하게 통합해 나가는 과정을 통해, 실제 IT 기업의 개발 프로세스와 원활한 커뮤니케이션 능력을 배양하고자 했습니다.
## 같이 개발한 팀원들
*  **[이강토] (팀장/Front/Back):** 
  * **[김도철] (Front/Back):** 로그인/회원가입/맴버쉽/쿠폰 부분, 마이페이지에서 각 페이지 링크 연결 및 모달로 간단 처리기능, 재가입방지/쿠폰재발급방지등
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
1. [Diagram](#diagram)
2. [와이어프레임](#와이어프레임)
3. [화면구현](#화면구현)
4. [주요 기능 (Key Features)](#주요-기능-key-features)
5. [서비스 화면 (Demo)](#서비스-화면-demo)
6. [프로젝트 보고서](#프로젝트-보고서)
7. [트러블 슈팅 (Trouble Shooting)](#트러블-슈팅-trouble-shooting)
8. [추후 추가하고싶은 기능](#추후-추가하고싶은-기능)
9. [회고](#회고)
## Diagram
<details>
<summary>usecase</summary>
<img width="784" height="587" alt="image" src="https://github.com/user-attachments/assets/5a62d987-a383-43b0-9d8c-9ff9a500bdbd" />
</details>

<details>
<summary>class</summary>
 <img width="1018" height="751" alt="image" src="https://github.com/user-attachments/assets/9cdf0220-2960-4e2a-91fb-6696670a923f" />
</details>

## 와이어프레임
<details>
<summary>메인 페이지</summary>
여기에 이미지를 넣어주세요
</details>
<details>
<summary>서브 페이지</summary>
여기에 이미지를 넣어주세요
</details>
<details>
<summary>마이 페이지</summary>
<img width="4848" height="10127" alt="마이페이지 와이어프레임" src="https://github.com/user-attachments/assets/703856cb-49e6-40bb-94e9-634a69adf030" />
</details>
<details>
<summary>로그인 페이지</summary>
<img width="373" height="446" alt="스크린샷 2026-04-28 113014" src="https://github.com/user-attachments/assets/0f5e893f-0910-4b04-b3c4-a30f93f352b0" />
</details>

## 화면구현
<details>
<summary>메인 페이지</summary>
<img width="1794" height="3321" alt="메인페이지2" src="https://github.com/user-attachments/assets/c0131ef7-33ad-418d-9077-e71133b2cc38" />
</details>
<details>
<summary>제품 페이지</summary>
여기에 이미지를 넣어주세요
</details>
<details>
<summary>품 상세 페이지</summary>
여기에 이미지를 넣어주세요
</details>
<details>
<summary>헤더 장바구니 패널</summary>
여기에 이미지를 넣어주세요
</details>
<details>
<summary>메인 장바구니 페이지</summary>
여기에 이미지를 넣어주세요
</details>
<details>
<summary>결제창</summary>
여기에 이미지를 넣어주세요
</details>
<details>
<summary>주문완료 페이지</summary>
여기에 이미지를 넣어주세요
</details>
<details>
<summary>비회원 주문조회</summary>
여기에 이미지를 넣어주세요
</details>
<details>
<summary>주문/배송 조회 페이지</summary>
여기에 이미지를 넣어주세요
</details>
<details>
<summary>주문 상세 페이지</summary>
여기에 이미지를 넣어주세요
</details>
<details>
<summary>마이 페이지</summary>
<img width="1794" height="1609" alt="마이페이지" src="https://github.com/user-attachments/assets/5e4ba072-7652-4059-9cc8-a8d2be498218" />
</details>
<details>
<summary>로그인/회원가 페이지</summary>
<img width="1794" height="1226" alt="로그인페이지" src="https://github.com/user-attachments/assets/16d690be-7a7d-47bd-9f30-a9ad0fa844b7" />
<img width="1794" height="1364" alt="회원가입페이지" src="https://github.com/user-attachments/assets/572b19a1-dc0d-4fa0-bc80-cdac768c45c5" />
</details>
<details>
<summary>고객지원 페이지</summary>
<img width="1794" height="1392" alt="고객지원페이지" src="https://github.com/user-attachments/assets/0bef93bd-6f56-4a5f-8cbf-a51566dcc530" />
</details>
<details>
<summary>FAQ 페이지</summary>
<img width="1014" height="1175" alt="127 0 0 1_5000_faq_board (1)" src="https://github.com/user-attachments/assets/de5d8f37-dd04-4bef-807c-b1a6c01336f0" />
</details>
<details>
<summary>회사 소개 페이지</summary>
<img width="1794" height="1915" alt="회사소개" src="https://github.com/user-attachments/assets/0ab23d32-f1e0-4ea5-879c-68fb31806f5d" />
</details>
<details>
<summary>1:1 문의 페이지</summary>
<img width="1014" height="1315" alt="127 0 0 1_5000_inquiry (1)" src="https://github.com/user-attachments/assets/38b27bec-ae40-46ec-ace1-5d5622f2fe17" />
</details>

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

## 서비스 화면 (Demo)
| 메가 메뉴 및 검색 | 장바구니 비동기 처리 |
| :---: | :---: |
|  |  |
| 카테고리 이동 및 직관적 검색 결과 | 새로고침 없는 실시간 수량/금액 변경 |

<br>

## 프로젝트 보고서

## 트러블 슈팅 (Trouble Shooting)

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
김도철
작업한 페이지 스타일을 꾸며보고 싶고 색감이나 전체적인 부분의 통일을 하고 싶다.(스타일 부분)

## 회고
김도철
 아이디어와 실제 구현 사이에는 생각보다 많은 디테일 차이가 있다는 것을 알게 되었습니다.
 처음에는 기능이 어느 정도 완성되면 프로젝트도 끝날 거라 생각했지만, 실제로는 하나의 기능이 마무리될 때마다 또 다른 디테일과 수정 사항이 계속해서 발생했고,
수업 시간 내용을 최대한 프로젝트에 적용하며, 처음에는 이해가 어려웠던 부분들도 작업을 진행하면서
Flask와 Jinja 템플릿 구조, 그리고 프론트엔드와 백엔드의 흐름을 자연스럽게 이해할 수 있게 되었습니다.
 또한 팀 프로젝트를 진행하며 팀장의 도움을 통해 많은 것을 배우게 되었고,
기능을 수정하고 디테일을 추가할수록 결과물이 점점 나아지는 과정을 직접 보며 개발에 더욱 몰입할 수 있었습니다.
아쉬운 점과 부족한 부분도 있었지만, 그보다 배운 점과 얻은 경험이 더 많은 의미 있는 프로젝트였다고 생각합니다.
