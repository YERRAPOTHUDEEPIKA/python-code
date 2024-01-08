let notification = document.getElementById('#notification');
        let successmsg = ' <ion-icon name="checkbox"></ion-icon> OTP Sent Successfully ! ';
        function showToast(msg){
            let toast = document.createElement('div');
            toast.classList.add('toast');
            toast.innerHTML = msg;   
            notification.appendChild(toast); 

            setTimeout(() => {
                toast.remove();
            }, 3000);
        }

function app(){

    
    return(

    )
}