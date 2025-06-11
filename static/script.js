// script.js

// =====================
// 전역 변수 설정
// =====================
const YEAR_START = 1920,
      YEAR_END   = 2030;

const PER_PAGE   = 10;  // 한 화면에 보여줄 항목 개수
const PAGE_BLOCK = 10;  // 한 블록에 보여줄 페이지 수

// =====================
// 각 필드별 코드 데이터
// =====================
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
  ],

  /*// 대표국적별 (국적별과 동일)
  sRepNationStr: [
    "한국","대만","말레이시아","북한","싱가포르","아프가니스탄","이란",
    "인도","중국","태국","이스라엘","필리핀","아랍에미리트연합국정부",
    "몽골","티베트","카자흐스탄","캄보디아","이라크","우즈베키스탄",
    "베트남","인도네시아","카타르","일본","홍콩",
    "베네수엘라","브라질","아르헨티나","콜롬비아","칠레","페루","우루과이","쿠바",
    "기타",
    "미국","멕시코","캐나다","자메이카","엘살바도르","트리니다드토바고",
    "케이맨제도","도미니카공화국",
    "호주","뉴질랜드","피지",
    "그리스","네덜란드","덴마크","독일","러시아","벨기에","스웨덴","스위스",
    "스페인","영국","오스트리아","이탈리아","체코","터키","포르투갈","폴란드",
    "프랑스","핀란드","헝가리","불가리아","보스니아","크로아티아","노르웨이",
    "에스토니아","아일랜드","잉글랜드","아이슬란드","루마니아","팔레스타인",
    "세르비아","룩셈부르크","북마케도니아","서독","알바니아","유고슬라비아",
    "몰타","우크라이나","슬로바키아",
    "남아프리카공화국","부탄","이집트","나이지리아","보츠와나","리비아",
    "모로코","케냐"
  ]*/
};

$(function(){
  // 0) 팝업 초기화
  $("#layerPopup").dialog({
    autoOpen:  false,
    modal:     true,
    width:     550,
    height:    450,
    resizable: false,
    draggable: true,
    closeText: "×",
    dialogClass: "code-search-dialog",
    buttons: [{
      text: "확인",
      class: "btn_blue2",
      click: function(){
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

  // 1) 코드 팝업 바인딩
  Object.keys(codeData).forEach(id => {
    $(`#${id}`).on("click", function(){
      renderOptions(codeData[id]);
      $("#chkAllChkBox").prop("checked", false);
      const title = $(this).closest(".item").find(".dot01").text() + " 검색결과";
      $("#layerPopup")
        .dialog("option","title", title)
        .data("target", `#${id}`)
        .dialog("open");
    });
  });

  // 2) 전체 선택 토글
  $(document).on("change","#chkAllChkBox", function(){
    $("#popupOptions tbody input[type=checkbox]").prop("checked", this.checked);
  });

  // 3) 상세검색 숨김 초기화
  $(".drop").hide();
  $(".btn_close").hide();
  $(".btn_more").show();
  $(".more").removeClass("open");

  // 4) 더보기 / 닫기
  $(".btn_more").on("click", ()=> {
    $(".drop").slideDown(200);
    $(".more").addClass("open");
    $(".btn_more").hide();
    $(".btn_close").show();
    $("[name=searchOpen]").val("Y");
  });
  $(".btn_close").on("click", ()=> {
    $(".drop").slideUp(200);
    $(".more").removeClass("open");
    $(".btn_close").hide();
    $(".btn_more").show();
    $("[name=searchOpen]").val("N");
  });

  // 5) 달력 위젯
  $(".datepicker, .tf_cal").datepicker({ dateFormat: "yy-mm-dd" });

  // 6) 제작연도 옵션 채우기
  for (let y=YEAR_START; y<=YEAR_END; y++) {
    $('select[name="sPrdtYearS"], select[name="sPrdtYearE"]')
      .append(`<option value="${y}">${y}</option>`);
  }

  // 7) 정렬 변경 즉시 재검색
  $("[name=sOrderBy]").on("change", function(){
    fn_changeOrder(this);
  });

  // 8) 영화명 인덱싱
  $(".list_idx").on("click","a", function(e){
    e.preventDefault();
    $("[name=chosung]").val($(this).text());
    $("[name=curPage]").val(1);
    $(".list_idx li").removeClass("on");
    $(this).parent().addClass("on");
    commSearchAjax();
  });

  // 9) 엔터키 검색
  $(document).on("keypress","form input[type=text]:enabled:not([readonly])", function(e){
    if(e.which===13){
      $("[name=curPage]").val(1);
      fn_searchList();
    }
  });
    commSearchAjax();
}); // <-- 여기까지 document.ready 닫힘

// 팝업 옵션 렌더링
function renderOptions(arr){
  const $tb = $("#popupOptions tbody").empty();
  for(let i=0; i<arr.length; i+=2){
    const L = arr[i], R = arr[i+1]||"";
    $tb.append(`
      <tr>
        <th><input type="checkbox" data-text="${L}"></th>
        <td>${L}</td>
        <th>${R?`<input type="checkbox" data-text="${R}">`:""}</th>
        <td>${R||""}</td>
      </tr>
    `);
  }
}

// 검색/초기화/페이징
function fn_searchList(type){
  const $f = $("#searchForm");

  $f.find("[name=curPage]").val(1);
  $f.find("[name=searchOpen]").val($(".btn_more").is(":hidden")?"Y":"N");
  const n=$("[name=sNomal]").prop("checked")?"Y":"N",
        m=$("[name=sMulti]").prop("checked")?"Y":"N",
        i=$("[name=sIndie]").prop("checked")?"Y":"N";
  $("[name=sMultiChk]").val(n+m+i);
  if(n+m+i==="NNN"){ alert("영화구분을 하나 이상 선택해주세요."); return; }
  commSearchAjax();
}
function fn_changeOrder(sel){
  $("[name=sOrderBy]").val($(sel).val());
  fn_searchList();
}

// 검색조건 초기화
	function fn_searchReset() {
		var $frm = $(document.searchForm);
		$frm.find("input:visible").val("");
		$frm.find("[name='sPrdtStatCd']").remove();
		$frm.find("[name='sMovTypeCd']").remove();
		$frm.find("[name='sGenreCd']").remove();
		$frm.find("[name='sGradeCd']").remove();
		$frm.find("[name='sShowTypeCd']").remove();
		$frm.find("[name='sNationCd']").remove();
		$frm.find("[name='chosung']").val("");
		$frm.find("input[type=checkbox]").prop("checked",true);
		$(".list_idx").children().removeClass("on");
		$("#sPrdtYearS").next().find(".slt_coverInner").text("--전체--");
		$("#sPrdtYearS").val("");
		$("#sPrdtYearE").next().find(".slt_coverInner").text("--전체--");
		$("#sPrdtYearE").val("");
		$("#useYn").next().find(".slt_coverInner").text("--전체--");
		$("#useYn").val("");

	}


function goPage(page){
  $("[name=curPage]").val(page);
  commSearchAjax();
}

// AJAX 로딩 + 클라이언트 페이징
function commSearchAjax(){
  $.ajax({
    url: "/movies/searchMovieList",
    type: "GET",
    data: $("#searchForm").serialize(),
    dataType: "json",
    beforeSend(){
      $(".tbl_comm tbody").html(
        `<tr><td colspan="10" class="tac">로딩 중...</td></tr>`
      );
    },
    success(data){
      console.log(data);
      console.log(Object.keys(data[0]||{}));
      const total = data.length;
      const page  = +$("[name=curPage]").val()||1;
      const pages = Math.ceil(total/PER_PAGE);
      const slice = data.slice((page-1)*PER_PAGE, page*PER_PAGE);


      // 테이블
      let html = slice.map(m=>`
        <tr>
          <td>${m.title_kr}</td><td>${m.title_en}</td><td>${m.movie_id}</td>
          <td>${m.year}</td><td>${m.country}</td><td>${m.type}</td>
          <td>${m.genres}</td><td>${m.status}</td><td>${m.director}</td><td>${m.production}</td>
        </tr>`).join("");
      if(!html) html = `<tr><td colspan="10">검색 결과가 없습니다.</td></tr>`;
      $(".tbl_comm tbody").html(html);
      $(".total em").text(total);

      // 2) 페이징 UI 생성
      const blockIdx = Math.floor((page-1)/PAGE_BLOCK);
      const startP   = blockIdx*PAGE_BLOCK + 1;
      const endP     = Math.min(startP+PAGE_BLOCK-1, pages);

      // 페이징
      const blk = Math.floor((page-1)/PAGE_BLOCK);
      const sP  = blk*PAGE_BLOCK+1;
      const eP  = Math.min(sP+PAGE_BLOCK-1,pages);
      let phtml = `<a class="btn first" href="javascript:goPage(1)"><span class="ico_comm">처음</span></a>`;
      phtml+= `<a class="btn prev" href="javascript:goPage(${sP>1?sP-1:1})"><span class="ico_comm">이전</span></a>`;
      phtml+= `<ul class="list_page">`;
      for(let p=sP;p<=eP;p++){
        phtml+=`<li><a href="javascript:goPage(${p})"${p===page?" class='on'":""}>${p}</a></li>`;
      }
      phtml+=`</ul><a class="btn next" href="javascript:goPage(${eP<pages?eP+1:pages})"><span class="ico_comm">다음</span></a>`;
      phtml+=`<a class="btn last" href="javascript:goPage(${pages})"><span class="ico_comm">마지막</span></a>`;
      $(".paging").html(phtml);
    },
    error(){
      $(".tbl_comm tbody").html(
        `<tr><td colspan="10" class="tac">조회 중 오류가 발생했습니다.</td></tr>`
      );
    }
  });
}