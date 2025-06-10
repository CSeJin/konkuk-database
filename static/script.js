// =====================
// script.js
// =====================

$(function(){

  // 1) 달력 위젯
  $(".datepicker").datepicker({
    dateFormat: "yy-mm-dd"
  });

  // 2) 제작연도 옵션 1920~2030
  for (let y = 1920; y <= 2030; y++) {
    $('select[name="sPrdtYearS"], select[name="sPrdtYearE"]')
      .append(`<option value="${y}">${y}</option>`);
  }

  // 3) 초기 숨김 상태
  $("#moreOptions").hide();
  $(".btn_close").hide();

  // 4) 더보기 / 닫기 토글
  $(".btn_more").on("click", function(){
    $("#moreOptions").slideDown(200);
    $(".btn_more").hide();
    $(".btn_close").show();
  });
  $(".btn_close").on("click", function(){
    $("#moreOptions").slideUp(200);
    $(".btn_close").hide();
    $(".btn_more").show();
  });

  // 5) 정렬 변경 시 즉시 재검색
  $("[name=sOrderBy]").on("change", function(){
    fn_changeOrder(this);
  });

});

// =====================
// 기본 검색 함수
// =====================
function fn_searchList(type){
  const $f = $("#searchForm");
  if(type === "excel"){
    if(!confirm("엑셀로 다운로드하시겠습니까? (데이터량이 많으면 오래 걸릴 수 있습니다)")) {
      return;
    }
    $f.attr("action","searchMovieListXls.do");
    $f.off("submit").submit();
    return;
  }
  // 페이지 초기화 & 검색 열림 상태 저장
  $f.find("[name=curPage]").val(1);
  $f.find("[name=searchOpen]").val( $(".btn_more").is(":hidden") ? "Y" : "N" );

  // 영화구분 3개 체크 여부
  const n = $("[name=sNomal]").prop("checked")? "Y":"N";
  const m = $("[name=sMulti]").prop("checked")? "Y":"N";
  const i = $("[name=sIndie]").prop("checked")? "Y":"N";
  $("[name=sMultiChk]").val(n+m+i);
  if(n+m+i === "NNN"){
    alert("영화구분은 한가지 이상 선택하셔야 조회 가능합니다.");
    return;
  }

  // AJAX 로 결과 가져오기
  commSearchAjax();
}

// =====================
// 초기화 버튼
// =====================
function fn_searchReset(){
  const $f = $("#searchForm");
  $f[0].reset();                       // 모든 input/select 기본값
  $f.find("[name=searchOpen]").val("Y");
  // 동적으로 추가된 hidden 코드값들 제거
  $f.find("input[name$='Cd']").remove();
  // 인덱싱 선택 제거
  $(".list_idx li a").removeClass("on");
}

// =====================
// 정렬 변경
// =====================
function fn_changeOrder(sel){
  $("[name=orderBy]").val( $(sel).val() );
  fn_searchList();
}

// =====================
// 페이징 함수
// =====================
function goPage(page){
  $("[name=curPage]").val(page);
  commSearchAjax();
}

// =====================
// AJAX 결과 렌더링
// =====================
function commSearchAjax(){
  $.ajax({
    type: "POST",
    url: $("#searchForm").attr("action"),
    data: $("#searchForm").serialize(),
    dataType: "html",
    beforeSend: function(){
      // 로딩 표시(취향껏)
      $(".rst_sch .tbl_comm tbody").html(`<tr><td colspan="10">로딩 중...</td></tr>`);
    },
    success: function(html){
      // 서버에서 전체 .rst_sch 영역만 돌려준다고 가정
      // 예: <div class="rst_sch">…</div>
      const $resp = $("<div>").append(html);
      // 1) 총 건수
      $(".rst_sch .total").html( $resp.find(".total").html() );
      // 2) 테이블 바디
      $(".tbl_comm tbody").html( $resp.find(".tbl_comm tbody").html() );
      // 3) 페이징
      $(".paging").html( $resp.find(".paging").html() );
      // 4) 인덱싱
      $(".item_idx").html( $resp.find(".item_idx").html() );
      // 5) 다시 토글 상태 반영
      if( $("[name=searchOpen]").val() === "N" ){
        $("#moreOptions").show();
        $(".btn_more").hide();
        $(".btn_close").show();
      } else {
        $("#moreOptions").hide();
        $(".btn_more").show();
        $(".btn_close").hide();
      }
    },
    error: function(){
      $(".tbl_comm tbody").html(`<tr><td colspan="10">데이터 조회 중 오류가 발생했습니다.</td></tr>`);
    }
  });
}