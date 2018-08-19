async function scroll_everything(page) {

  console.log('Scrolling through page');

  await page.evaluate(async () => {
    await new Promise((resolve, reject) => {
      try {
	const maxScroll = Number.MAX_SAFE_INTEGER;  
	let lastScroll = 0;
	const interval = setInterval(() => {
	  window.scrollBy(0, window.innerHeight);

	  const scrollTop = document.documentElement.scrollTop;
	  if (scrollTop === maxScroll || scrollTop === lastScroll) {
	    clearInterval(interval);
	    resolve();
	  } else {
	    lastScroll = scrollTop;
	  }
	}, 200);
      } catch (err) {
	console.log(err);
	reject(err.toString());
      }
    });
  });

  console.log('Finished scrolling');

}
