const YEAR_START = 1920,
      YEAR_END   = 2030;

const PER_PAGE   = 10;
const PAGE_BLOCK = 10;

const codeData = {
  // 제작상태
  sPrdtStatStr: [
    "개봉",
    "개봉예정",
    "개봉준비",
    "후반작업",
    "촬영진행",
    "촬영준비",
    "기타"
  ],

  // 유형
  sMovTypeStr: [
    "장편",
    "단편",
    "옴니버스",
    "온라인전용",
    "기타"
  ],

  // 장르별
  sGenreStr: [
    "드라마",
    "코미디",
    "액션",
    "멜로/로맨스",
    "스릴러",
    "미스터리",
    "공포(호러)",
    "어드벤처",
    "범죄",
    "가족",
    "판타지",
    "SF",
    "서부극(웨스턴)",
    "사극",
    "애니메이션",
    "다큐멘터리",
    "전쟁",
    "뮤지컬",
    "성인물(에로)",
    "공연",
    "기타"
  ],

  // 국적별
  sNationStr: [
    // 아시아
    "한국","대만","말레이시아","북한","싱가포르","아프가니스탄","이란",
    "인도","중국","태국","이스라엘","필리핀","아랍에미리트연합국정부",
    "몽골","티베트","카자흐스탄","캄보디아","이라크","우즈베키스탄",
    "베트남","인도네시아","카타르","일본","홍콩",
    // 중남미
    "베네수엘라","브라질","아르헨티나","콜롬비아","칠레","페루","우루과이","쿠바",
    // 기타
    "기타",
    // 북미주
    "미국","멕시코","캐나다","자메이카","엘살바도르","트리니다드토바고",
    "케이맨제도","도미니카공화국",
    // 오세아니아&태평양
    "호주","뉴질랜드","피지",
    // 유럽
    "그리스","네덜란드","덴마크","독일","러시아","벨기에","스웨덴","스위스",
    "스페인","영국","오스트리아","이탈리아","체코","터키","포르투갈","폴란드",
    "프랑스","핀란드","헝가리","불가리아","보스니아","크로아티아","노르웨이",
    "에스토니아","아일랜드","잉글랜드","아이슬란드","루마니아","팔레스타인",
    "세르비아","룩셈부르크","북마케도니아","서독","알바니아","유고슬라비아",
    "몰타","우크라이나","슬로바키아",
    // 아프리카
    "남아프리카공화국","부탄","이집트","나이지리아","보츠와나","리비아",
    "모로코","케냐"
  ]


};

$(function(){
  // 팝업 설정
  $("#layerPopup").dialog({
    autoOpen: false, modal: true, width: 550, height: 450,
    resizable: false, draggable: true,
    closeText: "×",
    dialogClass: "code-search-dialog",
    buttons: [{
      text: "확인", class: "btn_blue2", click: function(){
        const sel = [];
        $("#popupOptions tbody input:checked").each(function(){
          sel.push($(this).data("text"));
        });
        const tgt = $(this).data("target");
        $(tgt).val(sel.join(","));
        $(tgt).siblings("input[name$='Cd']").remove();
        const hidden = sel.map((t,i)=>
          `<input name="${$(tgt).attr("name")}Cd" type="hidden" value="CD${i}">`
        ).join("");
        $(tgt).after(hidden);
        $(this).dialog("close");
      }
    }]
  });

  // 팝업 바인딩
  Object.keys(codeData).forEach(id => {
    $(`#${id}`).on("click", function(){
      renderOptions(codeData[id]);
      $("#chkAllChkBox").prop("checked", false);
      const title = $(this).closest(".item").find(".dot01").text() + " 검색결과";
      $("#layerPopup").dialog("option", "title", title)
                      .data("target", `#${id}`).dialog("open");
    });
  });

  // 전체 선택
  $(document).on("change", "#chkAllChkBox", function(){
    $("#popupOptions tbody input[type=checkbox]").prop("checked", this.checked);
  });

  // 상세검색 초기화
  $(".drop").hide(); $(".btn_close").hide(); $(".btn_more").show(); $(".more").removeClass("open");

  $(".btn_more").on("click", ()=> {
    $(".drop").slideDown(200);
    $(".more").addClass("open");
    $(".btn_more").hide(); $(".btn_close").show();
    $("[name=searchOpen]").val("Y");
  });

  $(".btn_close").on("click", ()=> {
    $(".drop").slideUp(200);
    $(".more").removeClass("open");
    $(".btn_close").hide(); $(".btn_more").show();
    $("[name=searchOpen]").val("N");
  });

  // 달력
  $(".datepicker, .tf_cal").datepicker({ dateFormat: "yy-mm-dd" });

  // 제작연도 select
  for (let y = YEAR_START; y <= YEAR_END; y++) {
    $('select[name="sPrdtYearS"], select[name="sPrdtYearE"]').append(`<option value="${y}">${y}</option>`);
  }

  // 정렬 즉시 반영
  $("[name=sOrderBy]").on("change", function(){
    fn_changeOrder(this);
  });

  // 초성 인덱싱
  $(".list_idx").on("click", "a", function(e){
    e.preventDefault();
    $("[name=chosung]").val($(this).text());
    $("[name=curPage]").val(1);
    $(".list_idx li").removeClass("on");
    $(this).parent().addClass("on");
    commSearchAjax();
  });

  // 엔터 검색
  $(document).on("keypress", "form input[type=text]:enabled:not([readonly])", function(e){
    if (e.which === 13) {
      $("[name=curPage]").val(1);
      fn_searchList();
    }
  });

  // 초기 로딩
  commSearchAjax();
});

function renderOptions(arr){
  const $tb = $("#popupOptions tbody").empty();
  for(let i = 0; i < arr.length; i += 2){
    const L = arr[i], R = arr[i+1] || "";
    $tb.append(`
      <tr>
        <th><input type="checkbox" data-text="${L}"></th>
        <td>${L}</td>
        <th>${R ? `<input type="checkbox" data-text="${R}">` : ""}</th>
        <td>${R}</td>
      </tr>
    `);
  }
}

function fn_searchList(){
  const $f = $("#searchForm");
  $f.find("[name=curPage]").val(1);
  $f.find("[name=searchOpen]").val($(".btn_more").is(":hidden") ? "Y" : "N");

  const n = $("[name=sNomal]").prop("checked") ? "Y" : "N",
        m = $("[name=sMulti]").prop("checked") ? "Y" : "N",
        i = $("[name=sIndie]").prop("checked") ? "Y" : "N";
  $("[name=sMultiChk]").val(n + m + i);

  if (n + m + i === "NNN") {
    alert("영화구분을 하나 이상 선택해주세요.");
    return;
  }

  commSearchAjax();
}

function fn_searchReset() {
  const $f = $("#searchForm");

  // 1. 전체 입력 초기화
  $f[0].reset();

  // 2. 영화구분 체크박스 다시 체크 (기본값 YYY)
  $("[name=sNomal], [name=sMulti], [name=sIndie]").prop("checked", true);
  $("[name=sMultiChk]").val("YYY");

  // 3. 선택된 영화명 인덱싱 초기화
  $("[name=chosung]").val("");              // 히든 필드 초기화
  $(".list_idx li").removeClass("on");      // UI 표시 초기화

  // 4. 드롭다운 값 초기화
  $("#sPrdtYearS, #sPrdtYearE").val("");
  $("#sOrderBy").val("1"); // 정렬 기본값 최신순

  // 5. 다시 전체 리스트 조회
  fn_searchList();
}


function fn_changeOrder(sel){
  $("[name=sOrderBy]").val($(sel).val());
  fn_searchList();
}

function goPage(page){
  $("[name=curPage]").val(page);
  commSearchAjax();
}

function commSearchAjax(){
  $.ajax({
    url: "/movies/searchMovieList",
    type: "GET",
    data: $("#searchForm").serialize(),
    dataType: "json",
    beforeSend(){
      $(".tbl_comm tbody").html(`<tr><td colspan="10" class="tac">로딩 중...</td></tr>`);
    },
    success(data){

      const total = data.length;
      const page = +$("[name=curPage]").val() || 1;
      const pages = Math.ceil(total / PER_PAGE);
      const slice = data.slice((page - 1) * PER_PAGE, page * PER_PAGE);
      console.log("👉 받은 데이터 구조 확인", data[0]);

    console.log("🟢 첫 번째 데이터", slice[0]);
    console.log("✅ slice[0]", JSON.stringify(slice[0], null, 2));



      let html = slice.map(m => `
  <tr>
    <td>${m.title_kr || ''}</td>
    <td>${m.title_en || ''}</td>
    <td>${m.movie_id || ''}</td>
    <td>${m.year || ''}</td>
    <td>${m.nation_name || ''}</td>
    <td>${m.type || ''}</td>
    <td>${m.genres || ''}</td>
    <td>${m.status || ''}</td>
    <td>${m.director || ''}</td>
    <td>${m.production || ''}</td>
  </tr>
`).join("");



      if (!html) html = `<tr><td colspan="10">검색 결과가 없습니다.</td></tr>`;


      $(".tbl_comm tbody").html(html);
      $(".total em").text(total);
       console.log("✅ data 타입:", typeof data);
console.log("✅ data 배열 길이:", data.length);
console.log("✅ data[0] 내용:", data[0]);


      // 페이지 블럭 계산
      const blockIdx = Math.floor((page - 1) / PAGE_BLOCK);
      const startP = blockIdx * PAGE_BLOCK + 1;
      const endP = Math.min(startP + PAGE_BLOCK - 1, pages);

      let phtml = `<a class="btn first" href="javascript:goPage(1)"><span class="ico_comm">처음</span></a>`;
      phtml += `<a class="btn prev" href="javascript:goPage(${startP > 1 ? startP - 1 : 1})"><span class="ico_comm">이전</span></a>`;
      phtml += `<ul class="list_page">`;
      for (let p = startP; p <= endP; p++) {
        phtml += `<li><a href="javascript:goPage(${p})"${p === page ? " class='on'" : ""}>${p}</a></li>`;
      }
      phtml += `</ul><a class="btn next" href="javascript:goPage(${endP < pages ? endP + 1 : pages})"><span class="ico_comm">다음</span></a>`;
      phtml += `<a class="btn last" href="javascript:goPage(${pages})"><span class="ico_comm">마지막</span></a>`;
      $(".paging").html(phtml);
    },
    error(){
      $(".tbl_comm tbody").html(`<tr><td colspan="10" class="tac">조회 중 오류가 발생했습니다.</td></tr>`);
    }

  });
}
