import cv2

def light_removing(frame) :
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)
    L = lab[:,:,0]
    med_L = cv2.medianBlur(L,99) #median filter, 두번째 값은 커널의 크기이다. 필터를 적용해서 원본 이미지를 흐리게 만든다.
    invert_L = cv2.bitwise_not(med_L) #invert lightness, 배열의 모든 비트를 반전한다.
    composed = cv2.addWeighted(gray, 0.75, invert_L, 0.25, 0) # 오버레이를 만들어 준다. 회색으로 컨보트된 것을 모든 배열이 반전된 이미지 위에 올린다.
    return L, composed

