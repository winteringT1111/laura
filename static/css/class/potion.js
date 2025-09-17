// Get references to select content divs
const selectContentDivs = [
    document.querySelector('.select_content1'),
    document.querySelector('.select_content2'),
    document.querySelector('.select_content4'),
    document.querySelector('.select_content3')
];

let selectedItems = 0; // Track the number of selected items

// 아이템 조합에 넣기
function handleItemClick(item, itemImageSrc) {
    if (selectedItems < 4 && item.dataset.itemCount > 0) {
        // Display image in select_content divs
        selectContentDivs[selectedItems].innerHTML = `<img src="${itemImageSrc}" />`;

        // Reduce item count
        item.dataset.itemCount--;
        item.querySelector('p').textContent = `x${item.dataset.itemCount}`;
        selectedItems++;

        // Update modal with selected item details
        const selectedNames = document.querySelector('.selected');
        const selectedImages = document.querySelector('.selected_image');

        // Add item name and image to the modal
        const itemName = item.querySelector('.item_description p').textContent;
        const itemImage = `<img src="${itemImageSrc}" />`;
        selectedNames.innerHTML += `<span>${itemName}</span>`;
        selectedImages.innerHTML += `<span>${itemImage}</span>`;
    }
}

// Add event listeners to each item in item_wrap
document.querySelectorAll('.item').forEach(item => {
    const itemImageSrc = item.querySelector('img').src;
    item.dataset.itemCount = item.querySelector('p').textContent.replace('x', ''); // Initialize item count
    item.addEventListener('click', () => handleItemClick(item, itemImageSrc));
});

// 초기화 버튼
document.getElementById('initialize-btn').addEventListener('click', () => {
    selectContentDivs.forEach(div => div.innerHTML = '');
    selectedItems = 0;
    
    // Clear modal contents
    document.querySelector('.selected').innerHTML = '';
    document.querySelector('.selected_image').innerHTML = '';

    location.reload();
});


// 캐러셀 움직임
const prevButton = document.querySelector('.carousel-control-prev');
const nextButton = document.querySelector('.carousel-control-next');
const itemWrap = document.querySelector('.carousel-inner');
// 화살표 버튼 클릭 이벤트 처리
function handleCarouselTransition() {
    // 1초 동안 overflow hidden을 적용
    itemWrap.style.overflow = 'hidden';
    console.log("rgwwerg");

    // 1초 후에 overflow를 다시 기본값으로 변경
    setTimeout(() => {
        itemWrap.style.overflow = 'visible';  // 기본값 (혹은 원하는 상태로 변경)
    }, 1000);  // 1000ms = 1초
}

// 이전 버튼 클릭 시
prevButton.addEventListener('click', () => {
    handleCarouselTransition();
    // 추가적인 캐러셀 이동 로직 (예: 현재 슬라이드 이전으로 이동)
});

// 다음 버튼 클릭 시
nextButton.addEventListener('click', () => {
    handleCarouselTransition();
    console.log("rgwwsadfwefwfweerg");
    // 추가적인 캐러셀 이동 로직 (예: 현재 슬라이드 다음으로 이동)
});


document.addEventListener("DOMContentLoaded", function () {
    const makeBtn = document.querySelector('.make_btn');
    const selectContent2 = document.querySelector('.select_content2');

    // Initialize Bootstrap popover on makeBtn
    $(makeBtn).popover({
        container: 'body',
        placement: 'top',
        trigger: 'manual',
        content: '최소 2개의 아이템을 조합해주세요.'
    });

    makeBtn.addEventListener('click', () => {
        if (selectContent2.innerHTML.trim() === '') {
            // Show popover if no item is selected in .select_content2
            $(makeBtn).popover('show');
            setTimeout(() => $(makeBtn).popover('hide'), 2000); // Hide popover after 2 seconds
        } else {
            // Show modal if item is selected in .select_content2
            $('#staticBackdrop').modal('show');
        }
    });
});


document.addEventListener("DOMContentLoaded", function () {
    const submitButton = document.getElementById('submitButton');

    submitButton.addEventListener('click', () => {
        const selectedItems = Array.from(document.querySelectorAll('.selected span')).map(span => span.textContent);

        fetch("{% url 'main:check_combination' %}", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': '{{ csrf_token }}',
            },
            body: JSON.stringify({ selected_items: selectedItems }),
        })
        .then(response => response.json())
        .then(data => {
            $('#staticBackdrop').modal('hide'); // Hide the initial modal

            // Update result modal content based on the combination result
            const resultModalTitle = document.getElementById("resultModalTitle");
            const resultModalBody = document.getElementById("resultModalBody");
            const resultModalImage = document.getElementById("resultModalImage");

            if (data.result === "success") {
                resultModalTitle.textContent = "조합 성공!";
                resultModalBody.textContent = "정어리 파이를 획득했습니다!";
                resultModalImage.innerHTML = `<img src="/static/${data.image}" alt="Result Image">`;
            } else {
                resultModalTitle.textContent = "Better luck next time!";
                resultModalBody.textContent = "사용한 마법 재료가 전부 소진되었습니다.";
                resultModalImage.innerHTML = `<img src="/static/${data.image}" alt="Result Image">`;
            }
            $('#resultModal').modal('show');
        })
        .catch(error => console.error("Error:", error));
    });
});


document.getElementById('xbtn').addEventListener('click', () => {

    location.reload();
});