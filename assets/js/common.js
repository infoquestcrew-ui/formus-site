$(function () {
  var agent = navigator.userAgent.toLowerCase();
  var ipad =
    agent.indexOf("ipad") > -1 ||
    (agent.indexOf("macintosh") > -1 && "ontouchend" in document);
  if (ipad == true) {
    $('meta[name="viewport"]').attr("content", "width=1200px");
  }

  $(".l-header .menu").on("click", function () {
    $(this).toggleClass("open");
  });
  $(".l-header .toggle").on("click", function () {
    $(this).toggleClass("open");
  });
  $(".jsDropMenu").on("click", function () {
    $(this).toggleClass("open");
  });
  $(".jsModalClose").on("click", function () {
    $(".l-modal").hide();
  });

  //カレンダーのPlaceHolder
  $(".dateInput").on("input", function () {
    if ($(this).val()) {
      $(".spanMessage").hide(); // 日付が入力されたら非表示
    } else {
      $(".spanMessage").show(); // 日付がクリアされたら再表示
    }
  });

  //selectのPlaceholder

  $(".u-select").on("change", function () {
    if ($(this).val() === "") {
      $(this).addClass("select-empty").removeClass("select-filled");
    } else {
      $(this).addClass("select-filled").removeClass("select-empty");
    }
  });

  //toggle faq
  $(".faq_blk .faq-box dt").click(function () {
    $(this).toggleClass("show");
    $(this).next("dd").slideToggle();
  });
});
//fadein_logo
$(function () {
  setTimeout(function () {
    $(".load_fist .in-logo").fadeIn(1000);
  }, 500);
  setTimeout(function () {
    $(".load_fist").fadeOut(1000);
  }, 1000);
  $("nav a").click(function () {
    $(".menu ").removeClass("open");
  });
});

$(document).ready(function () {
  function checkDevice() {
    if (/Android|iPhone|iPad|iPod/i.test(navigator.userAgent)) {
      // スマホの場合の処理
      $(".merit2_blk .tit-cen")
        .off("click")
        .on("click", function () {
          $(this).toggleClass("show");
          $(this).next("p").slideToggle();
        });
    } else {
      // PCなど、スマホ以外のデバイスの場合の処理
      $(".merit2_blk .tit-cen").off("click");
      $(".merit2_blk .tit-cen p").show();
    }
  }

  // 初期読み込み時のデバイス判定
  checkDevice();

  // ウィンドウリサイズ時に再評価
  $(window).on("resize", function () {
    checkDevice();
  });

  //modall
  $(".modal").modaal({});

  //swiper
  var swiper = new Swiper(".mySwiper", {
    slidesPerView: "auto",
    scrollbar: {
      el: ".swiper-scrollbar",
    },
    navigation: {
      nextEl: ".swiper-button-next",
      prevEl: ".swiper-button-prev",
    },
  });

  //swiper
  var outlineSlides = new Swiper(".outlineSlides", {
    slidesPerView: "auto",
    navigation: {
      nextEl: ".swiper-button-next",
      prevEl: ".swiper-button-prev",
    },
    on: {
      init: function () {
        updateSlideNumber(this);
      },
      slideChange: function () {
        updateSlideNumber(this);
      },
    },
  });
  function updateSlideNumber(swiper) {
    var currentIndex = swiper.realIndex + 1; // スライドの現在のインデックス（1から始まる）
    var totalSlides = swiper.slides.length; // 全スライド数
    document.querySelector(
      ".slide-number"
    ).textContent = `${currentIndex}/${totalSlides}`;
  }
});

document.addEventListener("scroll", function () {
  const entryBlk = document.querySelector(".document_blk");
  const btn = document.querySelector(".btn-fix");

  if (entryBlk && btn) {
    const entryBlkOffset = entryBlk.offsetTop; // entryBlkのスクロール位置を取得
    const scrollPosition =
      window.pageYOffset || document.documentElement.scrollTop;

    if (scrollPosition > entryBlkOffset) {
      btn.classList.add("hidden");
    } else {
      btn.classList.remove("hidden");
    }
  }
});
