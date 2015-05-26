This is example on how to use BitPay API.

HTML:
<code>
<a href="#" id="id-bitpay-invoice" title="BitPay, the easy way to pay with bitcoins."><img src="https://bitpay.com/img/button5.png" alt="BitPay, the easy way to pay with bitcoins."></a>
<span id="id-bitpay-status"></span>
</code>

Javascript:
<code>
<script src='{{ media_url }}jquery.bitpay.js' type='text/javascript'></script>
<script>
$(document).ready(function(){

 $('#id-bitpay-invoice').click(function(){
  //
  // the following code queries RPC server and redirects user to bitpay.com website,
  // when invoice URL received
  //
  var bitpay = $.bitpay({'errorElementID': 'id-bitpay-status', 'rpc_url': '{% url rpc_bitpay_create_invoice %}', 'onSuccess': function(data){
    if(!('url' in data)){
      $('#id-bitpay-status').append('unexpected response from server.');
    }
    window.location.href=data.url;
  }, 'onFailure': function(){
    $('#id-bitpay-status').empty();
    $('#id-bitpay-status').append('<br/>Error');
  }});
  bitpay.generate_bitpay_invoice();
  return false;
 });

});
</script>
</code>

Python:
<code>
def rpc_bitpay_create_invoice(request):
    """
    Creates BitPay invoice. See tasks.py
    """
    task = BitPayInvoice()
    task.delay(self, order_id, price, desc, buyer_email, cart_id)
</code>