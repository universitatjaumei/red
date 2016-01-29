$(document).ready(function () {

  $('form button').click(function () {
    //socket.emit('deploy start event', {data: $("select option:selected").text()});
    showMessageDeploying();

    $.ajax({
      type: 'POST',
      url: $('form.deploy-form').attr('action'),
      data: JSON.stringify(getSelectedProject(), null, '\t'),
      contentType: 'application/json;charset=UTF-8',
      success: function (data, status) {
        showMessageDeployFinished();
      },

      error: function (error) {
        showMessageErrorDeploying();
      },
    });

    return false;
  });

  fillProjectBranches(getSelectedProject());

  $('select[name=app]').change(function () {
    fillProjectBranches(getSelectedProject());
  });
});
