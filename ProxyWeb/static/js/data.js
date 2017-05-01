function update_status(series, lang)
{
    var container = $("#flot-line-chart-moving");
    $.ajax({
        url:'/api/status',
        type:'GET',
        dataType:'json',
    })
    .done(function(data){
        $("#alert-notification").hide();
        $('#available_proxies').html(data.availables);
        $('#rookie_proxies').html(data.rookies);
        $('#currents').html(data.currents);
        $('#lost_proxies').html(data.losts);
        $('#dead_proxies').html(data.deads);

        series[0].data.push([0, data.availables]);
        series[1].data.push([0, data.rookies]);
        series[2].data.push([0, data.currents]);
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
        if(lang == 'english')
        {
            $("#alert-notification").show();
            $('#available_proxies').html('Unknown');
            $('#rookie_proxies').html('Unknown');
            $('#currents').html('Unknown');
            $('#lost_proxies').html('Unknown');
            $('#dead_proxies').html('Unknown');
        }
        else
        {
            $("#alert-notification").show();
            $('#available_proxies').html('未知');
            $('#rookie_proxies').html('未知');
            $('#currents').html('未知');
            $('#lost_proxies').html('未知');
            $('#dead_proxies').html('未知');
        }
    });
}

$(document).ready(function(){
    var arr,reg=new RegExp("(^| )lang=([^;]*)(;|$)");
    arr=document.cookie.match(reg)
    var lang = unescape(arr[2]);
    if(lang == 'english')
    {
        var series = [
            {
                label: "Available proxies",
                color: "rgb(28, 122, 180)",
                data: [],
                lines: {show:true},
                points: {show:true},
            },
            {
                label: "New proxies",
                color: "rgb(76, 184, 98)",
                data: [],
                lines: {show:true},
                points: {show:true},
            },
            {
                label: "Current jobs",
                color: "rgb(246, 173, 89)",
                data: [],
                lines: {show:true},
                points: {show:true},
            },
        ];
    }
    else
    {
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
        ];
    }
setInterval(function(){update_status(series, lang)}, 1000);
});
