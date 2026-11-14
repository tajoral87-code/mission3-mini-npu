
# 미션 3 - Mini NPU Simulator

import json
import math
import re
import time

EPSILON = 1e-9


# 1. MAC 연산
def mac(pattern, filter_data):
    score = 0.0

    for i in range(len(pattern)):
        for j in range(len(pattern[i])):
            score += pattern[i][j] * filter_data[i][j]

    return score


# 2. 점수 판정
def decide(score_a, score_b, label_a="A", label_b="B"):
    if abs(score_a - score_b) < EPSILON:
        return "UNDECIDED"

    if score_a > score_b:
        return label_a

    return label_b


# 3. 3x3 사용자 입력
def input_matrix(name):
    matrix = []
    print(f"\n{name} (3줄 입력, 공백 구분)")

    while len(matrix) < 3:
        row_number = len(matrix) + 1

        try:
            values = input(f"{row_number}행: ").split()

            if len(values) != 3:
                print("입력 오류: 숫자 3개를 입력하세요.")
                continue

            row = [float(value) for value in values]

            if not all(math.isfinite(value) for value in row):
                print("입력 오류: 유한한 숫자만 입력하세요.")
                continue

            matrix.append(row)

        except ValueError:
            print("입력 오류: 숫자만 입력하세요.")

    return matrix


# 4. 라벨 정규화
def normalize_label(label):
    if not isinstance(label, str):
        return None

    label = label.strip().lower()

    if label in ("+", "cross"):
        return "Cross"

    if label == "x":
        return "X"

    return None


# 5. JSON 배열 크기와 숫자 검증
def validate_matrix(matrix, size):
    if not isinstance(matrix, list) or len(matrix) != size:
        raise ValueError(f"행 개수 불일치: {size}행 필요")

    for row_number, row in enumerate(matrix, start=1):
        if not isinstance(row, list) or len(row) != size:
            raise ValueError(
                f"{row_number}행 열 개수 불일치: {size}열 필요"
            )

        for value in row:
            if isinstance(value, bool) or not isinstance(
                value, (int, float)
            ):
                raise ValueError("숫자가 아닌 값 발견")

            if not math.isfinite(value):
                raise ValueError("유효하지 않은 숫자 발견")


# 6. MAC 연산 시간 측정
def measure_time(pattern, filter_data, repeats=10):
    start = time.perf_counter()

    for _ in range(repeats):
        mac(pattern, filter_data)

    end = time.perf_counter()

    return (end - start) * 1000 / repeats


# 7. 테스트용 십자가 패턴 자동 생성
def create_cross(size):
    matrix = []

    for i in range(size):
        row = []

        for j in range(size):
            if i == size // 2 or j == size // 2:
                row.append(1.0)
            else:
                row.append(0.0)

        matrix.append(row)

    return matrix


# 보너스 1. 2차원 배열을 1차원 배열로 변환
def flatten_matrix(matrix):
    result = []

    for row in matrix:
        for value in row:
            result.append(value)

    return result


# 보너스 1. 1차원 MAC 계산
def mac_flat(pattern, filter_data):
    score = 0.0

    for i in range(len(pattern)):
        score += pattern[i] * filter_data[i]

    return score


# 보너스 2. X 패턴 자동 생성
def create_x(size):
    matrix = []

    for i in range(size):
        row = []

        for j in range(size):
            if i == j or i + j == size - 1:
                row.append(1.0)
            else:
                row.append(0.0)

        matrix.append(row)

    return matrix


# 보너스 1. 기존 방식과 최적화 방식 성능 비교
def compare_performance(repeats=10):
    print("\n[보너스 1] 2D / 1D MAC 성능 비교")
    print(f"{'크기':<10}{'2D(ms)':>14}{'1D(ms)':>14}{'결과':>12}")

    for size in [3, 5, 13, 25]:
        pattern = create_cross(size)
        filter_data = create_x(size)

        flat_pattern = flatten_matrix(pattern)
        flat_filter = flatten_matrix(filter_data)

        score_2d = mac(pattern, filter_data)
        score_1d = mac_flat(flat_pattern, flat_filter)

        times_2d = []
        times_1d = []

        for _ in range(repeats):
            start = time.perf_counter()
            mac(pattern, filter_data)
            times_2d.append((time.perf_counter() - start) * 1000)

            start = time.perf_counter()
            mac_flat(flat_pattern, flat_filter)
            times_1d.append((time.perf_counter() - start) * 1000)

        avg_2d = sum(times_2d) / repeats
        avg_1d = sum(times_1d) / repeats

        result = (
            "PASS"
            if abs(score_2d - score_1d) < EPSILON
            else "FAIL"
        )

        print(
            f"{size}x{size:<7}"
            f"{avg_2d:>14.6f}"
            f"{avg_1d:>14.6f}"
            f"{result:>12}"
        )


# 보너스 2. 패턴 자동 생성 및 판정
def bonus_mode():
    print("\n[보너스 2] 패턴 자동 생성기")

    while True:
        try:
            size = int(input("패턴 크기 N (3~25, 홀수): "))

            if 3 <= size <= 25 and size % 2 == 1:
                break

            print("3부터 25까지 홀수를 입력하세요.")

        except ValueError:
            print("정수를 입력하세요.")

    cross = create_cross(size)
    x_pattern = create_x(size)

    print("\nCross 패턴")
    for row in cross:
        print(" ".join(str(int(value)) for value in row))

    print("\nX 패턴")
    for row in x_pattern:
        print(" ".join(str(int(value)) for value in row))

    score_cross = mac(cross, cross)
    score_x = mac(cross, x_pattern)

    print("\n[생성된 Cross 패턴 판정]")
    print(f"Cross 점수: {score_cross}")
    print(f"X 점수: {score_x}")
    print(f"판정: {decide(score_cross, score_x, 'Cross', 'X')}")


# 8. 성능 분석
def performance_analysis(sizes):
    print("\n[성능 분석: MAC 10회 평균]")
    print(f"{'크기':<10}{'평균 시간(ms)':>17}{'연산 횟수':>14}")
    print("-" * 41)

    for size in sizes:
        pattern = create_cross(size)
        filter_data = create_cross(size)

        average = measure_time(pattern, filter_data)

        print(
            f"{size}x{size:<7}"
            f"{average:>17.6f}"
            f"{size * size:>14}"
        )


# 9. 모드 1: 사용자 입력
def mode1():
    print("\n[1] 필터 입력")

    filter_a = input_matrix("필터 A")
    filter_b = input_matrix("필터 B")

    print("\n필터 A:", filter_a)
    print("필터 B:", filter_b)
    print("필터 저장 완료!")

    print("\n[2] 패턴 입력")
    pattern = input_matrix("패턴")

    score_a = mac(pattern, filter_a)
    score_b = mac(pattern, filter_b)

    result = decide(score_a, score_b)

    print("\n[3] MAC 연산 결과")
    print(f"A 점수: {score_a}")
    print(f"B 점수: {score_b}")
    print(f"판정: {result}")

    performance_analysis([3])


# 10. 모드 2: JSON 분석
def mode2():
    print("\n[1] JSON 파일 로드")

    try:
        with open("data.json", "r", encoding="utf-8") as file:
            data = json.load(file)

    except (FileNotFoundError, json.JSONDecodeError, OSError) as error:
        print(f"파일 오류: {error}")
        return

    if not isinstance(data, dict):
        print("JSON 오류: 최상위 데이터가 객체가 아닙니다.")
        return

    filters = data.get("filters")
    patterns = data.get("patterns")

    if not isinstance(filters, dict) or not isinstance(patterns, dict):
        print("JSON 오류: filters 또는 patterns 구조가 잘못되었습니다.")
        return

    print("data.json 로드 완료!")

    for size in (5, 13, 25):
        key = f"size_{size}"
        status = "있음" if key in filters else "없음"
        print(f"필터 {key}: {status}")

    print("\n[2] 패턴 분석")

    total = 0
    passed = 0
    failed_cases = []

    for case_name, case in patterns.items():
        total += 1
        print(f"\n--- {case_name} ---")

        try:
            match = re.fullmatch(r"size_(\d+)_(\d+)", case_name)

            if match is None:
                raise ValueError("패턴 키 형식 오류")

            size = int(match.group(1))
            filter_key = f"size_{size}"

            if not isinstance(case, dict):
                raise ValueError("패턴 데이터 구조 오류")

            if filter_key not in filters:
                raise ValueError("해당 크기의 필터 없음")

            filter_group = filters[filter_key]

            if not isinstance(filter_group, dict):
                raise ValueError("필터 데이터 구조 오류")

            normalized_filters = {}

            for name, matrix in filter_group.items():
                label = normalize_label(name)

                if label is None:
                    raise ValueError(f"알 수 없는 필터: {name}")

                if label in normalized_filters:
                    raise ValueError(f"중복 필터 라벨: {label}")

                normalized_filters[label] = matrix

            if set(normalized_filters) != {"Cross", "X"}:
                raise ValueError("Cross 또는 X 필터 누락")

            pattern = case.get("input")
            expected = normalize_label(case.get("expected"))

            if expected is None:
                raise ValueError("expected 라벨 오류")

            validate_matrix(pattern, size)
            validate_matrix(normalized_filters["Cross"], size)
            validate_matrix(normalized_filters["X"], size)

            cross_score = mac(pattern, normalized_filters["Cross"])
            x_score = mac(pattern, normalized_filters["X"])

            result = decide(
                cross_score, x_score, "Cross", "X"
            )

            print(f"Cross 점수: {cross_score:.16f}")
            print(f"X 점수: {x_score:.16f}")

            if result == expected:
                passed += 1
                print(f"판정: {result} | expected: {expected} | PASS")

            else:
                if result == "UNDECIDED":
                    reason = "동점(epsilon) 판정"
                else:
                    reason = f"판정 불일치: {result} != {expected}"

                failed_cases.append((case_name, reason))
                print(
                    f"판정: {result} | expected: {expected} "
                    f"| FAIL ({reason})"
                )

        except (ValueError, TypeError, KeyError) as error:
            reason = str(error)
            failed_cases.append((case_name, reason))
            print(f"FAIL: {reason}")

    performance_analysis([3, 5, 13, 25])

    print("\n[4] 결과 요약")
    print(f"총 테스트: {total}개")
    print(f"통과: {passed}개")
    print(f"실패: {len(failed_cases)}개")

    if failed_cases:
        print("\n실패 케이스:")

        for case_name, reason in failed_cases:
            print(f"- {case_name}: {reason}")

    else:
        print("실패 케이스 없음")
     
    compare_performance()
    

# 11. 메인 메뉴

# 메인 메뉴
def main():
    print("=== Mini NPU Simulator ===")
    print("1. 사용자 입력 (3x3)")
    print("2. data.json 분석")
    print("3. 보너스: 패턴 자동 생성")

    while True:
        choice = input("선택: ").strip()

        if choice == "1":
            mode1()
            break

        elif choice == "2":
            mode2()
            break

        elif choice == "3":
            bonus_mode()
            break

        else:
            print("1, 2 또는 3을 선택하세요.")


if __name__ == "__main__":
    main()
