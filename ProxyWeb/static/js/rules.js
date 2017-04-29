function submit_form(rule_method)
{
    $.ajax({
        url:'/api/rules/'+rule_method,
        type:'POST',
        data: $('#rule_form').serialize(),
    })
    .done(function(data){
        if(data == 'fail')
            alert('请检查表单');
        else
            setTimeout('window.location.reload()', 2000);
    });
    $('#rule_modal').modal('hide');
}
$(document).ready(function(){
    $('.crawlers').click(function(){
        var rule_name = $(this).parents('tr').attr('rule-name');
        var crawler_method = $(this).attr('crawler-method');
        $.ajax({
            url:'/api/crawlers/'+crawler_method+'/'+rule_name,
            type:'GET',
        })
            .done(function(){
                window.location.reload();
            });
    });
    $('.rules').click(function(){
        var rule_method = $(this).attr('rule-method');
        if(rule_method == 'delete')
        {
            var rule_name = $(this).attr('rule-name');
            $.ajax({
                url:'/api/rules/delete/'+rule_name,
                type:'GET',
            })
                .done(function(data){
                    if(data == 'Not finished')
                        alert('删除规则前请先停止对应爬虫');
                    else if(data == 'Timeout')
                        alert('删除超时，请重试');
                    else if(data == 'Succeed')
                        alert('删除成功');
                    else
                        alert('未知错误');
                    window.location.reload();
                });
        }
        else if(rule_method == 'update')
        {
            var rule_name = $(this).attr('rule-name');
            $.ajax({
                url:'/rules/'+rule_name,
                type:'GET',
            })
                .done(function(data){
                    $('#rule_modal').html(data);
                    $('#rule_modal').modal('show');
                });
        }
        else if(rule_method == 'add')
        {
            $.ajax({
                url:'/rules/',
                type:'GET',
            })
                .done(function(data){
                    $('#rule_modal').html(data);
                    $('#rule_modal').modal('show');
                });
        }
    });
});
