
$(document).on('click', '.view_receipt', function(){
  var order_id = $(this).attr('id');
  $.ajax({
    url: "/viewreceipt",
    method: "POST",
    data:{order_id:order_id},
    success:function(b_data){
        var order_data = JSON.parse(b_data);
        order_data.forEach((element, index) => {
         
          
      });
        
      }
    })
});
