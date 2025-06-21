import streamlit as st
import random
import time
import pandas as pd
import plotly.express as px

# --- Streamlit 페이지 설정 (가장 위에 있어야 함) ---
st.set_page_config(
    page_title="RetireGuard: 은퇴 자금 시뮬레이터",
    page_icon="💰", # 탭에 표시될 아이콘
    layout="wide", # 넓은 레이아웃 사용
    initial_sidebar_state="expanded" # 사이드바 기본 확장
)

# --- CSS 스타일 추가 (조금 더 깔끔하게) ---
st.markdown("""
<style>
    .stApp {
        background-color: #f0f2f6; /* 배경색 */
        color: #333333; /* 기본 글자색 */
    }
    .stButton>button {
        background-color: #4CAF50; /* 버튼 배경색 */
        color: white; /* 버튼 글자색 */
        border-radius: 8px; /* 버튼 모서리 둥글게 */
        padding: 10px 20px;
        font-size: 16px;
    }
    .stButton>button:hover {
        background-color: #45a049;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #2c3e50; /* 제목 색상 */
    }
    .stAlert { /* 알림창 색상 조정 */
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)


# --- 사이드바 (Sidebar) 설정 ---
with st.sidebar:
    # st.image("your_logo.png", use_column_width=True) # 여기에 로고 이미지 경로를 넣어주세요
    st.markdown("## 💰 RetireGuard")
    st.write("---")
    st.markdown("### 당신의 은퇴 계획을 시뮬레이션 해보세요!")
    st.markdown("현재 재정 상태와 목표를 입력하면, AI 몬테카를로 시뮬레이션으로 은퇴 자금의 지속 가능성을 예측해 드립니다.")
    st.write("---")
    st.info("💡 **알림**: 본 시뮬레이션 결과는 예측이며, 실제와 다를 수 있습니다. 참고 자료로 활용해주세요.")


# --- 메인 콘텐츠 영역 ---
st.title("RetireGuard: 당신의 빛나는 은퇴를 위한 AI 재정 시뮬레이터")
st.markdown("#### 불확실한 미래, 예측 가능한 은퇴 계획으로 대비하세요.")

# --- 1. 사용자 입력 받기 ---
st.header("1. 당신의 현재 상황과 은퇴 목표를 알려주세요")
col1, col2 = st.columns(2) # 2개의 컬럼으로 나누기

with col1:
    current_age = st.number_input("현재 나이 (세):", min_value=18, max_value=80, value=40, help="현재 당신의 나이를 입력해주세요.")
    current_savings = st.number_input("현재 보유하신 은퇴/투자 자금 (만원):", min_value=0.0, value=50000.0, help="현재 보유한 총 자산을 만원 단위로 입력해주세요.")
    pre_retirement_monthly_savings = st.number_input("은퇴 전 매월 추가 저축액 (만원):", min_value=0.0, value=100.0, help="은퇴 전까지 매월 추가로 저축할 금액을 입력해주세요.")

with col2:
    target_retirement_age = st.number_input("목표 은퇴 나이 (세):", min_value=current_age + 1, max_value=90, value=60, help="몇 살에 은퇴하고 싶으신가요?")
    monthly_expenses = st.number_input("은퇴 후 예상 월 생활비 (만원):", min_value=0.0, value=250.0, help="은퇴 후 한 달에 필요한 예상 생활비를 입력해주세요.")
    annual_fixed_pension = st.number_input("은퇴 후 연간 고정 연금 수령액 (만원, 국민연금 등):", min_value=0.0, value=1200.0, help="국민연금, 개인연금 등 은퇴 후 매년 고정적으로 받을 수입을 입력해주세요. (예: 월 100만원이면 1200 입력)")

# 은퇴 후 목표 연령 계산 (시뮬레이션 종료 연령)
target_post_retirement_years = st.number_input("은퇴 후 자금이 지속되기를 바라는 목표 연수 (년):", min_value=1, max_value=100, value=30, help="은퇴 후 몇 년 동안 자금이 고갈되지 않기를 원하시나요?")
target_end_age = target_retirement_age + target_post_retirement_years

st.header("2. 투자 및 물가 가정")
col3, col4 = st.columns(2)
with col3:
    annual_investment_return = st.number_input("예상 연간 평균 투자 수익률 (%):", min_value=-10.0, max_value=30.0, value=5.0, help="자산을 투자했을 때 예상되는 연평균 수익률을 입력해주세요.")
with col4:
    annual_inflation_rate = st.number_input("예상 연간 평균 물가 상승률 (%):", min_value=0.0, max_value=10.0, value=2.0, help="매년 물가가 얼마나 오를지 예상되는 %를 입력해주세요.")


# --- 3. 시뮬레이션 시작 버튼 ---
st.markdown("---")
if st.button("🚀 은퇴 계획 시뮬레이션 시작", help="입력된 정보를 바탕으로 은퇴 자금 지속 확률을 계산합니다."):
    # 입력값 검증 (간단하게)
    if current_age >= target_retirement_age:
        st.warning("현재 나이가 은퇴 목표 나이보다 많거나 같습니다. 은퇴 전 기간 시뮬레이션은 자동으로 건너뜁니다.")
        pre_retirement_years = 0
    else:
        pre_retirement_years = target_retirement_age - current_age
        st.info(f"✨ 은퇴까지 남은 기간: **{pre_retirement_years}년** 동안 자산을 증식합니다.")

    # --- 4. 시뮬레이션 설정 및 초기화 ---
    annual_investment_return_decimal_avg = annual_investment_return / 100
    annual_inflation_rate_decimal_avg = annual_inflation_rate / 100

    investment_volatility = 0.10  # 투자 수익률 변동성 (예: +/- 10%)
    inflation_volatility = 0.01   # 물가 상승률 변동성 (예: +/- 1%)

    num_simulations = 5000  # 시뮬레이션 반복 횟수
    successful_scenarios = 0 # 자금 고갈 없이 목표 연수 도달한 시나리오 수
    
    # 각 시뮬레이션 시나리오의 자금 고갈 연도를 저장할 리스트
    depletion_years = [] 
    # 각 시뮬레이션 시나리오의 최종 자금 잔액을 저장할 리스트
    final_savings_list = []
    # --- 각 시나리오의 연도별 자산 경로를 저장할 리스트 (새로 추가) ---
    all_scenario_paths = [] 

    st.write(f"\n--- ⏳ {num_simulations}회 몬테카를로 시뮬레이션 실행 중... ---")
    progress_bar = st.progress(0, text="시뮬레이션 진행 중...")


    # --- 5. 메인 몬테카를로 루프 ---
    for i in range(num_simulations):
        scenario_current_age = current_age
        scenario_remaining_savings = current_savings
        scenario_current_annual_expenses = monthly_expenses * 12 # 연간으로 변환
        scenario_annual_fixed_pension = annual_fixed_pension
        
        # --- 각 시나리오의 연도별 자산을 기록할 리스트 초기화 ---
        current_scenario_path = [] 
        # 시작 자산 기록 (현재 나이 & 초기 자산)
        current_scenario_path.append({'Age': scenario_current_age, 'Savings': scenario_remaining_savings, 'Type': 'Pre-Retirement Path'})

        # --- 5.1. 은퇴 전 기간 시뮬레이션 ---
        for year_pre in range(pre_retirement_years):
            annual_actual_return_pre = random.uniform(
                annual_investment_return_decimal_avg - investment_volatility,
                annual_investment_return_decimal_avg + investment_volatility
            )
            scenario_remaining_savings += pre_retirement_monthly_savings * 12 # 연간 저축액 추가
            scenario_remaining_savings *= (1 + annual_actual_return_pre) # 투자 수익 반영
            scenario_current_age += 1 # 나이 증가
            current_scenario_path.append({'Age': scenario_current_age, 'Savings': scenario_remaining_savings, 'Type': 'Pre-Retirement Path'})


        # --- 5.2. 은퇴 후 기간 시뮬레이션 ---
        is_depleted = False # 이 시나리오에서 자금이 고갈되었는지 여부
        
        while scenario_remaining_savings > 0 and scenario_current_age < target_end_age:
            annual_actual_return = random.uniform(
                annual_investment_return_decimal_avg - investment_volatility,
                annual_investment_return_decimal_avg + investment_volatility
            )
            annual_actual_inflation = random.uniform(
                annual_inflation_rate_decimal_avg - inflation_volatility,
                annual_inflation_rate_decimal_avg + inflation_volatility
            )

            # 연간 지출 (물가 반영 및 연금 수령액 차감)
            current_year_expenses_after_inflation = scenario_current_annual_expenses * (1 + annual_actual_inflation)
            net_annual_expense = current_year_expenses_after_inflation - scenario_annual_fixed_pension
            
            scenario_remaining_savings -= net_annual_expense

            if scenario_remaining_savings > 0:
                scenario_remaining_savings *= (1 + annual_actual_return)
            else: # 자금 고갈
                is_depleted = True
                depletion_years.append(scenario_current_age - target_retirement_age + 1) # 은퇴 후 몇 년차에 고갈
                current_scenario_path.append({'Age': scenario_current_age, 'Savings': 0, 'Type': 'Post-Retirement Path'}) # 자금 고갈 시 0으로 기록
                break # 자금 고갈 시 현재 시나리오 중단

            scenario_current_annual_expenses = current_year_expenses_after_inflation # 다음 해를 위한 생활비 업데이트
            scenario_current_age += 1 # 나이 증가
            current_scenario_path.append({'Age': scenario_current_age, 'Savings': scenario_remaining_savings, 'Type': 'Post-Retirement Path'})
        
        # --- 각 시나리오의 결과 기록 및 경로 저장 ---
        if not is_depleted and scenario_current_age >= target_end_age: # 성공 시나리오
            successful_scenarios += 1
            final_savings_list.append(scenario_remaining_savings) # 성공 시나리오의 최종 자금 저장
            # 성공 시나리오 경로에 '성공' 태그 추가
            for item in current_scenario_path:
                item['Result'] = 'Success'
            all_scenario_paths.append(current_scenario_path) # 성공 경로 저장

        elif is_depleted: # 자금 고갈 시나리오
            final_savings_list.append(scenario_remaining_savings)
            # 실패 시나리오 경로에 '실패' 태그 추가
            for item in current_scenario_path:
                item['Result'] = 'Failure'
            all_scenario_paths.append(current_scenario_path) # 실패 경로 저장
        else: # 목표 연수 미달성 (자금 남아있음)
            final_savings_list.append(scenario_remaining_savings)
            # 미달성 시나리오 경로에 '미달성' 태그 추가 (성공으로 간주하지 않음)
            for item in current_scenario_path:
                item['Result'] = 'Partial Failure' # 또는 'Incomplete'
            all_scenario_paths.append(current_scenario_path)

        # 진행 바 업데이트
        progress_bar.progress((i + 1) / num_simulations)

    # 모든 시뮬레이션 경로를 하나의 데이터프레임으로 통합 (그래프를 위해)
    # 이 부분은 다음 단계에서 자세히 다룰 것입니다.

    # --- 6. 최종 몬테카를로 결과 출력 ---
    success_rate = (successful_scenarios / num_simulations) * 100

    st.markdown("---")
    st.header("✨ 은퇴 시뮬레이션 결과")
    st.markdown(f"**당신의 은퇴 계획이 {target_retirement_age}세에 은퇴하여 {target_end_age}세까지 지속될 확률은 <u><span style='color:#FF4B4B; font-size:30px;'>{success_rate:.2f}%</span></u> 입니다.**", unsafe_allow_html=True)


    if success_rate >= 80:
        st.success("🎉 **축하합니다!** 이 계획은 매우 튼튼해 보입니다. 지금처럼 잘 관리해 나가시면 안정적인 노후를 보내실 수 있을 거예요.")
    elif success_rate >= 60:
        st.info("💡 **조정 고려**: 이 계획은 성공 가능성이 높습니다. 하지만 조금 더 안정적인 노후를 위해 저축액 증가, 지출 감소, 또는 투자 전략 조정을 고려해 볼 수 있습니다.")
    elif success_rate >= 30:
        st.warning("🤔 **위험 신호**: 이 계획은 중간 정도의 위험을 가지고 있습니다. 자금 고갈 위험을 줄이기 위해 저축액 증가, 지출 감소, 은퇴 시기 조정 등 강력한 재조정이 필요합니다.")
    else:
        st.error("⚠️ **즉각적 조치 필요!**: 이 계획은 고갈 위험이 매우 높습니다. 시급히 재정 계획을 재조정하고, 필요한 경우 재무 전문가와 상담하는 것을 강력히 추천합니다.")

    st.markdown("---")
    st.subheader("📊 시뮬레이션 결과 분석")

    # --- 새로 추가할 연도별 자산 변화 그래프를 위한 코드 (다음 단계에서 추가) ---
    # all_paths_df = pd.DataFrame([item for sublist in all_scenario_paths for item in sublist])
    # # 성공/실패 시나리오 몇 개만 샘플링하여 그래프 그리기
    # success_paths = [path for path in all_scenario_paths if path[0]['Result'] == 'Success']
    # failure_paths = [path for path in all_scenario_paths if path[0]['Result'] == 'Failure']
    #
    # num_sample_paths = min(5, len(success_paths), len(failure_paths)) # 각 5개씩 샘플링
    #
    # sampled_paths_data = []
    # for j in range(num_sample_paths):
    #     for item in success_paths[j]:
    #         sampled_paths_data.append({'Scenario': f'Success {j+1}', 'Age': item['Age'], 'Savings': item['Savings']})
    #     if failure_paths: # 실패 시나리오가 있을 경우에만 추가
    #         for item in failure_paths[j]:
    #             sampled_paths_data.append({'Scenario': f'Failure {j+1}', 'Age': item['Age'], 'Savings': item['Savings']})
    #
    # if sampled_paths_data:
    #     sampled_df = pd.DataFrame(sampled_paths_data)
    #     fig_paths = px.line(sampled_df, x='Age', y='Savings', color='Scenario',
    #                         title='대표 시나리오별 연도별 자산 변화',
    #                         labels={'Age': '나이', 'Savings': '자산 잔액 (만원)'},
    #                         hover_name='Scenario')
    #     fig_paths.add_vline(x=target_retirement_age, line_width=2, line_dash="dash", line_color="red", annotation_text="은퇴 나이")
    #     fig_paths.add_vline(x=target_end_age, line_width=2, line_dash="dash", line_color="blue", annotation_text="목표 종료 나이")
    #     st.plotly_chart(fig_paths, use_container_width=True)
    # else:
    #     st.info("시뮬레이션 경로를 그릴 데이터가 부족합니다.")


    # 자금 고갈 연도 분포 시각화 (기존)
    if depletion_years: 
        depletion_df = pd.DataFrame(depletion_years, columns=['Years to Depletion'])
        st.write(f"총 {len(depletion_years)}개의 시나리오에서 자금이 고갈되었습니다.")
        depletion_df = depletion_df[depletion_df['Years to Depletion'] >= 0] 

        if not depletion_df.empty:
            fig_depletion = px.histogram(depletion_df, x='Years to Depletion',
                                        title='자금이 고갈된 시나리오별 지속 연수 분포 (은퇴 후)',
                                        labels={'Years to Depletion': '은퇴 후 자금 지속 연수'},
                                        nbins=max(10, int(target_post_retirement_years / 5)), 
                                        height=400,
                                        color_discrete_sequence=['#4CAF50']) 
            st.plotly_chart(fig_depletion, use_container_width=True)
        else:
            st.info("시뮬레이션 결과, 모든 시나리오에서 자금이 고갈되지 않았습니다!")
    else:
        st.info("시뮬레이션 결과, 모든 시나리오에서 자금이 고갈되지 않았습니다!")
    
    # 최종 자금 잔액 분포 시각화 (기존)
    if final_savings_list:
        final_savings_df = pd.DataFrame(final_savings_list, columns=['Final Savings'])
        fig_final_savings = px.histogram(final_savings_df, x='Final Savings',
                                        title='시나리오별 최종 자금 잔액 분포 (만원)',
                                        labels={'Final Savings': '최종 자금 잔액 (만원)'},
                                        height=400,
                                        color_discrete_sequence=['#2196F3']) 
        st.plotly_chart(fig_final_savings, use_container_width=True)


    st.markdown("---")
    st.info("""
        💡 **팁**: 성공 확률이 낮다면 다음 사항을 고려해 보세요.
        - **은퇴 전 매월 추가 저축액**을 늘려 은퇴 자금을 더 확보합니다.
        - **은퇴 후 예상 월 생활비**를 줄여 지출을 통제합니다.
        - **목표 은퇴 나이**를 늦춰 은퇴 전 자산 증식 기간을 늘립니다.
        - **예상 연간 평균 투자 수익률**을 높이는 전략을 고려합니다 (단, 위험이 커질 수 있습니다).
        - **은퇴 후 자금이 지속되기를 바라는 목표 연수**를 현실적으로 조정합니다.
        각 변수를 변경하여 시뮬레이션을 다시 실행해 보세요!
    """)