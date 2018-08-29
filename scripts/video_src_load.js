// 
// Fetch video source file. Allows for playback of video in e.g. INstagram captures.
//
async function video_src_load(page) {
  await page.$$eval('video[src]', async ss => {
    const noop = () => {}
    const doFetch = url => fetch(url).catch(noop)
    for (let i = 0; i < ss.length; i++) {
      const video_url = ss[i].src
      await doFetch(video_url)
    }
  })
}

