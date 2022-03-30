// function to add table row
function addRow() {
    var tableBody = document.getElementById('billingtable').getElementsByTagName('tbody')[0];
    var rowCount = tableBody.rows.length;  // table horizontal row count.
    var tr = tableBody.insertRow(rowCount); // insert a row below the previous row.

    for (var c = 0; c < 6; c++) {
        var td = document.createElement('td'); 
        td = tr.insertCell(c);
        tr.setAttribute("class","item-row")

        if (c == 0) {     
            var element = document.createElement('input');
            element.setAttribute('type', 'text');
            element.setAttribute('class','form-control product_input')
            element.setAttribute("list","products")
            td.appendChild(element);
        }
        else if(c==1){
            var element = document.createElement('input');
            element.setAttribute('type', 'number');
            element.setAttribute('readonly','')
            element.setAttribute('class','form-control current_qty')
            td.appendChild(element)
        }
        else if(c==2){
            var element = document.createElement('input');
            element.setAttribute('type', 'number');
            element.setAttribute('class','form-control dispensequantity')
            td.appendChild(element)
        }
        else if(c==3){
            var element = document.createElement('input');
            element.setAttribute('type', 'number');
            element.setAttribute('class','form-control selling_price')
            element.setAttribute('readonly','')
            td.appendChild(element)
        }
        else if(c==4){
            var element = document.createElement('input');
            element.setAttribute('type', 'number');
            element.setAttribute('class','form-control total')
            element.setAttribute('readonly','')
            td.appendChild(element)
        }
        else{
            var button = document.createElement('input');
            button.setAttribute('type', 'button');
            button.setAttribute('value', 'Remove');
            button.setAttribute('tabindex','16');
            button.setAttribute('onclick', 'removeRow(this)');
            button.setAttribute('class','btn btn-danger btn-sm row-remove')
            td.appendChild(button);
        }
    }  
}
// function to remove table row
function removeRow(oButton) {
    var empTab = document.getElementById('billingtable');
    var total = parseFloat(oButton.parentNode.parentNode.children[4].children[0].value)
    empTab.deleteRow(oButton.parentNode.parentNode.rowIndex); 
    document.getElementById("total_sum_value").value -= total
    var subTotal = $(".subtotal").val()
    var payment = $(".payment").val()
    var change = parseFloat(payment)- parseFloat(subTotal)
    if( change >= 0){
        $(".change").val(change)
    }
    else{
        $(".change").val(0)
    }
}
// This function checks if there is a change on product name field, change the current quantity and selling_price
$(document).on('change', '.product_input', function(){
var productName = $(this).val();
let productId = $('#products [value="' + productName + '"]').data('value');
var currentQty = this.parentNode.parentNode.children[1].children[0]
var sellingPrice = this.parentNode.parentNode.children[3].children[0]
$.ajax({
    url: "/productsdetails",
    method: "POST",
    data:{productId:productId},
    success:function(b_data){
        var product_data = JSON.parse(b_data)
        currentQty.value = product_data[0]['current_qty'];
        sellingPrice.value = product_data[0]['selling_price'];
        }
    })
});

$('#billingtable').on("keyup","input" ,function(e) {
var element=e.target;
if(element.matches("input.dispensequantity")){
    var quantity = element.value
    var unitCost = element.parentNode.parentNode.children[3].children[0].value
    var totalValue = parseFloat(quantity) * parseFloat(unitCost)
    if( isNaN(parseFloat(totalValue))){
        element.parentNode.parentNode.children[4].children[0].value = 0;
    }
    else{
        element.parentNode.parentNode.children[4].children[0].value = totalValue
    }
}
else if (element.matches("input.selling_price")){
    var unitCost = element.value;
    var quantity = element.parentNode.parentNode.children[2].children[0].value
    var totalValue = parseFloat(quantity) * parseFloat(unitCost)

    if( totalValue == ''){
        element.parentNode.parentNode.children[4].children[0].value = 0;
    }
    else{
        element.parentNode.parentNode.children[4].children[0].value = totalValue
        $(".subtotal").value += totalValue
    }
}
else if (element.matches("input.payment")){
    var payment = element.value;
    var subTotal = $(".subtotal").val()
    var change = parseFloat(payment)- parseFloat(subTotal)
    if( change >= 0){
        $(".change").val(change)
    }
    else{
        $(".change").val(0)
    }
}

var sum_total_values = 0;
$("#billingtable .total").each(function () {
    
    if (isNaN($(this).val())){
        console.log("true")
        var get_total_value = 0;
        sum_total_values += parseFloat(get_total_value);
    }
    else{
        var get_total_value = $(this).val();
        sum_total_values += parseFloat(get_total_value);
    }
})
// append the sum_total_values to subtotal
if (isNaN($(".subtotal").val())){
    $(".subtotal").val(0)
}
else{
    $(".subtotal").val(sum_total_values)
}

var subTotal = $(".subtotal").val()
var payment = $(".payment").val()
var change = parseFloat(payment)- parseFloat(subTotal)
if( change >= 0){
    $(".change").val(change)
}
else{
    $(".change").val(0)
}
});

// Send data to backend
$(".sendData").click(function(e) {
    var arrayItem = [];
    var customerDetails = [];
    let customerName = $(".customer_name").val();
    let paidAmount = $(".payment").val();
    if (customerName ===""){
        arrayItem.length = 0
        customerDetails.length = 0
        alert("Customer Name is Required")

    }
    else if (paidAmount ===""){
        arrayItem.length = 0
        customerDetails.length = 0
       alert("Paid amount is Required")
   }
    else{
        let customerId = $('#customers [value="' + customerName + '"]').data('value');
        let purchaseDate = $(".payment_date").val();
        let paymentType = $(".payment_type").val();
        let subTotal = $(".subtotal").val();
        let paidAmount = $(".payment").val();
        let change = $(".change").val();
        let customerItem = {
            CustomerId: customerId,
            PurchaseDate: purchaseDate,
            PaymentType: paymentType,
            Subtotal: subTotal,
            PaidAmount: paidAmount,
            changeGiven: change
        }
    customerDetails.push(customerItem)
    }
    $.each($("#insert_purchase .item-row"), function(index, value){
        let productName = $(this).find(".product_input").val();
        let productId = $('#products [value="' + productName + '"]').data('value');
        let qty = $(this).find(".dispensequantity").val()
        let unitprice = $(this).find(".selling_price").val()
        let total = $(this).find(".total").val()

        if (productName === "" ){
            // empty the lists
            arrayItem.length = 0
            customerDetails.length = 0
            alert("Product/Service Name is Required")
        }
        else if (qty ===""){
             // empty the lists
             arrayItem.length = 0
             customerDetails.length = 0
            alert("Quantity is Required")
        }
       
        else{
            let item = {
                ProductId: productId,
                ProductQty: qty,
                ProductCost: unitprice,
                ProductTotalAmount: total,
                }
                arrayItem.push(item)  
        }
    });
    // check if the array is empty
    if (arrayItem.length === 0 ){
    }
    if (customerDetails.length === 0){
    }
    else{
        sArrayItem = JSON.stringify(arrayItem);
        scustomerDetails = JSON.stringify(customerDetails);
        $.ajax({
            url: "/addbillitems",
            method: "POST",
            data:{customerDetails:scustomerDetails, ArrayItem:sArrayItem},
            success:function(b_data){
              if (b_data == 'success') {
                  window.location = "/billing";
                  $('#insert_purchase').fadeOut(1200).fadeIn(1200);
                // alert("Data imeen")
              }
            }
          })
    }
})
    

