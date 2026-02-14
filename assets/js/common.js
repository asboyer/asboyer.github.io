function showCopiedToast() {
    var toast = document.getElementById("email-copied-toast");
    if (!toast) {
        toast = document.createElement("div");
        toast.id = "email-copied-toast";
        toast.textContent = "copied to clipboard";
        document.body.appendChild(toast);
    }
    toast.classList.add("show");
    setTimeout(function () {
        toast.classList.remove("show");
    }, 1800);
}

$(document).ready(function () {
    $(".email-copy").on("click", function () {
        var eu = $(this).data("eu");
        var ed = $(this).data("ed");
        var email = eu + "@" + ed;
        if (navigator.clipboard) {
            navigator.clipboard.writeText(email).then(showCopiedToast);
        } else {
            var ta = document.createElement("textarea");
            ta.value = email;
            ta.style.cssText = "position:fixed;opacity:0";
            document.body.appendChild(ta);
            ta.select();
            document.execCommand("copy");
            document.body.removeChild(ta);
            showCopiedToast();
        }
    });

    // add toggle functionality to abstract and bibtex buttons
    $("a.abstract").click(function () {
        $(this).parent().parent().find(".abstract.hidden").toggleClass("open");
        $(this).parent().parent().find(".bibtex.hidden.open").toggleClass("open");
    });
    $("a.bibtex").click(function () {
        $(this).parent().parent().find(".bibtex.hidden").toggleClass("open");
        $(this).parent().parent().find(".abstract.hidden.open").toggleClass("open");
    });
    $("a").removeClass("waves-effect waves-light");

    // bootstrap-toc
    if ($("#toc-sidebar").length) {
        var navSelector = "#toc-sidebar";
        var $myNav = $(navSelector);
        Toc.init($myNav);
        $("body").scrollspy({
            target: navSelector,
        });
    }

    // add css to jupyter notebooks
    const cssLink = document.createElement("link");
    cssLink.href = "../css/jupyter.css";
    cssLink.rel = "stylesheet";
    cssLink.type = "text/css";

    let theme = localStorage.getItem("theme");
    if (theme == null || theme == "null") {
        const userPref = window.matchMedia;
        if (userPref && userPref("(prefers-color-scheme: dark)").matches) {
            theme = "dark";
        }
    }

    $(".jupyter-notebook-iframe-container iframe").each(function () {
        $(this).contents().find("head").append(cssLink);

        if (theme == "dark") {
            $(this).bind("load", function () {
                $(this).contents().find("body").attr({
                    "data-jp-theme-light": "false",
                    "data-jp-theme-name": "JupyterLab Dark",
                });
            });
        }
    });
});
