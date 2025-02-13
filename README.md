# TireAutoSNP

사용방법

1. omniwheel_ref 폴더에 odb 추가
2. main.py 실행
3. ./postprocessing/filter_doe.py 파일 내의    " doe_results_path = './postprocessing/result/Total_sampling_DOE.csv' " 부분 doe csv파일 경로로 변경
4. ./postprocessing/doe_results_extractor.py 실행
5. results/ 폴더 내에 성능평가 요소와 그에 해당하는 doe csv파일들이 생성되었는지 확인

* 새로운 odb를 추가하고 싶을 시, 해당하는 odb만 main.py 코드 실행하여 성능평가 요소 추출하고, 2-3-4-5 프로세스 반복