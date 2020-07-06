$(document).ready(() => {
    let table;
    table = new Tabulator("#results-table", {
        height: "311px",
        pagination: "local",
        paginationSize: 10,
        layout: "fitColumns",
        placeholder: "No hay resultados",
        columns: [
            {title: "", field: "index", width: 40},
            {
                title: "",
                field: "url",
                formatter: "link",
                formatterParams: {labelField: "alias", target: "_blank"},
            },
            {
                title: "",
                field: "local",
                formatter: "link",
                formatterParams: {label: "En cache", urlPrefix: "http://127.0.0.1:5000", target: "_blank"},
            },
        ],
    });

    $("#query-button").click(function () {
        executeQuery();
    });

    function executeQuery() {
        queryString = $("#query-text").val();
        // console.log(queryString);

        $.ajax({
            type: "GET",
            url: "http://127.0.0.1:5000/executeQuery",
            data: {
                query_string: queryString,
            },
            success: handleSuccess,
            error: handleError,
        });
    }

    function handleError(jqXHR, textStatus, error) {
        // The 1st is the JQuery XHR object. The 2nd is the text status of the error. The 3rd is the error itself.
        // console.log(error);
    }

    function handleSuccess(data) {
        let parsedResp = JSON.parse(data);
        // console.log(parsedResp);
        let documentsIndexes = Object.keys(parsedResp);
        let documentsArray = [];
        let queryTime = null;
        documentsIndexes.forEach((index) => {
            let elem = parsedResp[index];
            // console.log(elem);
            if (index !== "query_time") {
                elem["index"] = Number.parseInt(index) + 1;
                documentsArray.push(elem);
            } else {
                queryTime = elem;
            }
        });

        // console.log(documentsArray);

        if (documentsArray.length > 0) {
            table.setData(documentsArray);
            $("#results-count").html(documentsArray.length);
            if (!!queryTime) {
                $("#query-time").html(`${queryTime} segundos`);
            }
        } else {
            table.setData();
            $("#results-count").html(0);
            if (!!queryTime) {
                $("#query-time").html(`${queryTime} segundos`);
            }
        }
    }
});
