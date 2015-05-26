/*
* jquery.bitpay
*
* Allows to query your server, that creates BitPay invoice.
*/

(function($){

$.bitpay = function(options){
 if ( typeof(options) == "undefined" || options == null ) { options = {}; };

 var jBitpay = {
    options: $.extend({
	    errorElementID: '',
	    rpc_url: '',
	    form_id: '',
	    task_timeout: 1000,
	    attempts: 15,
            onSuccess: function(){ },
	    onFailure: function(){ },
    }, options),
    error_happened: function(msg){
	var message = "Error loading content.";
	if(msg!=undefined){
	    message = msg;
	}
        $('#'+jBitpay.errorElementID).empty();
        $('#'+jBitpay.errorElementID).append('<span class="err">'+message+'</span>');
    },
    loading_message_show: function(){
        $('#'+jBitpay.options.errorElementID).empty();
        $('#'+jBitpay.options.errorElementID).append('<span style="color:green;">'+'Loading..'+'</span>');
    },
    get_json: function(data, callback, error_callback){
     $.ajax({
	url: jBitpay.options.rpc_url,
	cache: false,
	dataType: 'json',
	data: data,
	success: function(data, status){
	    if(data&&(data=='failure'||(data.hasOwnProperty('error')))){
		if(!error_callback){
		  jBitpay.error_happened();
		} else {
		  error_callback();
		}
		return;
	    } else {
		$('#failure').hide();
	    }
	    if(callback) callback(data, status);
	}
     }).fail(function(jqxhr, textStatus, error){
	var err = textStatus + ', ' + error + '. Reload page ?';
	if(error!='') jBitpay.error_happened(err);
     });
    },
    reset_defaults: function(){
      jBitpay.options.form_id='';
      jBitpay.options.attempts=15;
    },
    bitpay_rpc: function(args, callback){
      var params = []
      if(args){
	for(k in args){
	  params.push({'name': k, 'value': args[k]});
	}
      }
      if(jBitpay.options.form_id.length>0){
	params.push({'name': 'form-id', 'value': jBitpay.options.form_id});
      } else {
	jBitpay.loading_message_show();
      }
      jBitpay.get_json(params, function(data,status){
       if(data=='wait'){ // wait until status becomes available
        if(jBitpay.options.attempts==0||data.form_id!=undefined){
	    jBitpay.reset_defaults();
	    $('#'+jBitpay.options.errorElementID).append('<span class="err">Invoice generating task do not respond.</span>');
        } else {
         jBitpay.options.attempts = jBitpay.attempts - 1;
         setTimeout(jBitpay.bitpay_rpc, jBitpay.options.task_timeout);
        }
        return false;
       } else {
          if(data&&data.form_id){
	    jBitpay.options.form_id=data.form_id;
            jBitpay.bitpay_rpc();
	  } else {
	   jBitpay.reset_defaults();
	   if(jBitpay.options.onSuccess) jBitpay.options.onSuccess(data);
	  }
       }
      }, function(data){
	  jBitpay.error_happened('Infrastructure Controller returned error.');
	  if(jBitpay.options.onFailure) jBitpay.options.onFailure();
      });
    },
    generate_bitpay_invoice: function(){
      jBitpay.bitpay_rpc();
    },
 };
 return {
    generate_bitpay_invoice: jBitpay.generate_bitpay_invoice,
 };
};
})(jQuery);
