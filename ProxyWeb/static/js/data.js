var container = $("#flot-line-chart-moving");
function update_status(series)
{
    $.ajax({
        url:'/api/status',
        type:'GET',
        dataType:'json',
    })
    .done(function(data){
        $("#alert-notification").hide();
        $('#available_proxies').html(data.availables);
        $('#rookie_proxies').html(data.rookies);
        $('#futures').html(data.futures);
        $('#lost_proxies').html(data.losts);
        $('#dead_proxies').html(data.deads);

        series[0].data.push([0, data.availables]);
        series[1].data.push([0, data.rookies]);
        series[2].data.push([0, data.futures]);
        //series[3].data.push([0, data.deads]);
        for(var i = 0; i < series.length; i++)
        {
            series[i].data = series[i].data.slice(-20);
            for(var j = 0; j < series[i].data.length; j++)
                series[i].data[j][0] = j;
        }
        $.plot(container, series);
    })
    .fail(function(){
        $("#alert-notification").show();
        $('#available_proxies').html('未知');
        $('#rookie_proxies').html('未知');
        $('#futures').html('未知');
        $('#lost_proxies').html('未知');
        $('#dead_proxies').html('未知');
    });
}

$(document).ready(function(){
    var series = [
        {
            label: "可用代理数",
            color: "rgb(28, 122, 180)",
            data: [],
            lines: {show:true},
            points: {show:true},
        },
        {
            label: "新发现代理数",
            color: "rgb(76, 184, 98)",
            data: [],
            lines: {show:true},
            points: {show:true},
        },
        {
            label: "当前任务数",
            color: "rgb(246, 173, 89)",
            data: [],
            lines: {show:true},
            points: {show:true},
        },
//        {
//            label: "失效代理数",
//            color: "rgb(226, 84, 83)",
//            data: [],
//            lines: {
//                fill: false
//            }
//        },
    ];
    setInterval(function(){update_status(series)}, 1000);
});
