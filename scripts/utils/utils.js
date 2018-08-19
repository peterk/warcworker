module.exports.delay = function (time = 5000) {
  return new Promise(resolve => {
    setTimeout(resolve, time);
  })
}
