
$(document).ready(function(){	

	var stripeFormModule = $('.stripe-payment-form')
	var stripeFormDataToken = stripeFormModule.attr('data-token')
	var stripeFormDataNextUrl = stripeFormModule.attr('data-next-url')

	var stripeTemplate = $.templates("#stripeTemplate")
	var stripeTemplateContext = {
		publish_key: stripeFormDataToken,
		next_url: stripeFormDataNextUrl
	}

	var stripeTemplateHtml = stripeTemplate.render(stripeTemplateContext)

	stripeFormModule.html(stripeTemplateHtml)



	// Create a Stripe client.
	var paymentForm=$('.payment-form')

	if (paymentForm.length>1){
		alert("Only one payment form is allowed")
		paymentForm.css('display','none')
	}
	else if (paymentForm.length==1){

			var pubKey = paymentForm.attr('data-token')
			var nextUrl = paymentForm.attr('data-next-url')

			var stripe = Stripe(pubKey);

			// Create an instance of Elements.
			var elements = stripe.elements();

			// Custom styling can be passed to options when creating an Element.
			// (Note that this demo uses a wider set of styles than the guide below.)
			var style = {
			  base: {
			    color: '#32325d',
			    lineHeight: '18px',
			    fontFamily: '"Helvetica Neue", Helvetica, sans-serif',
			    fontSmoothing: 'antialiased',
			    fontSize: '16px',
			    '::placeholder': {
			      color: '#aab7c4'
			    }
			  },
			  invalid: {
			    color: '#fa755a',
			    iconColor: '#fa755a'
			  }
			};

			// Create an instance of the card Element.
			var card = elements.create('card', {style: style});

			// Add an instance of the card Element into the `card-element` <div>.
			card.mount('#card-element');

			// Handle real-time validation errors from the card Element.
			card.addEventListener('change', function(event) {
			  var displayError = document.getElementById('card-errors');
			  if (event.error) {
			    displayError.textContent = event.error.message;
			  } else {
			    displayError.textContent = '';
			  }
			});

			// Handle form submission.
			var form = $('#payment-form');
			var btnLoad = form.find('.btn-load')

			var errorHtml = "<i class='fa fa-warning'></i> An error occured"
			var errorClasses = "btn btn-danger disabled my-3"
			var loadingHtml = "<i class='fa fa-spin fa-spinner'></i>Loading..."
			var loadingClasses = "btn btn-success disabled my-3"

			var defaultHtml = btnLoad.html()
			var defaultClasses = btnLoad.attr("class")


			form.on('submit', function(event) {
			  event.preventDefault();
			  
			  btnLoad.blur()
			  var loadTime = 1500
			  var currentTimeout;
			  

			  stripe.createToken(card).then(function(result) {
			    if (result.error) {
			      // Inform the user if there was an error.
			      var errorElement = $('#card-errors');
			      errorElement.textContent = result.error.message;
			      currentTimeout = displayBtnStatus(
			      						btnLoad,
			      						errorHtml,
			      						errorClasses,
			      						1000
			      						)
			    } else {
			      // Send the token to your server.
			      currentTimeout = displayBtnStatus(
			      						btnLoad,
			      						loadingHtml,
			      						loadingClasses,
			      						1000
			      						)
			      stripeTokenHandler(nextUrl, result.token);
			    }
			  });
			});

			function displayBtnStatus(element, newHtml, newClasses, loadTime){
				//var defaultHtml = element.html()
				//var defaultClasses = element.attr("class")

				return setTimeout(function(){
									element.html(newHtml)
									element.removeClass(defaultClasses)
									element.addClass(newClasses)
								}, loadTime)
				}

			function redirectToNext(nextPath){
				if (nextPath){
					setTimeout(function(){
						window.location.href=nextPath
					},1500)
				}
			}

			function stripeTokenHandler(nextUrl, token){
				//console.log(token.id)
				var paymentMethodEndpoint='/billing/payment-method/create/'
				var data={'token':token.id}
				$.ajax({
					data:data,
					url:paymentMethodEndpoint,
					method:"POST",
					success:function(data){
						var successMsg=data.message || "Success! Payment method added"
						card.clear()
						console.log(data)
						if (nextUrl){
							console.log(successMsg)
							successMsg=successMsg+"<br/><br/><i class='fa fa-spin fa-spinner'></i> Redirecting...."
						}
						if($.alert){
							$.alert(successMsg)
						} else {
							alert(successMsg)
						}
						btnLoad.html(defaultHtml)
						btnLoad.attr('class',defaultClasses)

						redirectToNext(nextUrl)

					},
					error: function(error){
						console.log(error)
					}
				})
			}
	}
}
)