var targetNode = document.getElementById('messages-responses');

var config = { childList: true };

var callback = function(mutationsList, observer) {
    for(var mutation of mutationsList) {
        if (mutation.type === 'childList') {
            var element = document.getElementById('messages-container');
            element.scrollTop = element.scrollHeight;
        }
    }
};

var observer = new MutationObserver(callback);

observer.observe(targetNode, config);