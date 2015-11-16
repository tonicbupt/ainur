$(document).ready(function() {
    $('.form-submit').each(function(i, e) {
        e.onsubmit = function() { return false; };
        var form = $(e);
        form.find('.submitter').click(function(e) {
            var btn = $(this);
            btn.attr('disabled', 'disabled');
            form.find('.error-reason').text('');
            form.find('.error-detail').text('');
            $.ajax({
                url: form.data('url'),
                type: form.data('method') || 'GET',
                data: form.serialize(),
                success: function(r) {
                    btn.removeAttr('disabled');
                    if (btn[0].success) {
                        btn[0].success(r);
                    }
                },
                error: function(r) {
                    btn.removeAttr('disabled');
                    var c = JSON.parse(r.responseText);
                    form.find('.error-reason').text('出错原因: ' + c.reason);
                    if (c.detail) {
                        form.find('.error-detail').append('详细信息: ' + c.detail);
                    }
                    if (c.missing) {
                        form.find('.error-detail').append('缺少参数: ' + c.missing);
                    }
                }
            });
        });
    });
});
