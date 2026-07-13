/**
 * 学习时长自动跟踪工具
 * 用于自动记录用户在学习页面上的停留时间
 */

// 配置常量
const TRACKING_INTERVAL = 30 * 1000; // 30秒（毫秒）- 每30秒检查一次
const MIN_STUDY_TIME = 0.008; // 最小记录时长（小时），即30秒 - 缩短为30秒以便更快记录
const STAGE_COMPLETION_REWARD = 0.5; // 完成一个学习阶段奖励的学习时长（小时）
const DISPLAY_UPDATE_INTERVAL = 5 * 1000; // 5秒更新一次显示（实时显示）

// 全局状态
let pageEnterTime = null; // 页面进入时间
let lastRecordTime = null; // 上次记录时间
let trackingTimer = null; // 定时器
let displayTimer = null; // 显示更新定时器
let accumulatedTime = 0; // 累计的未记录时长（毫秒）
let isPageVisible = true; // 页面是否可见
let currentRecordCallback = null; // 当前记录回调函数
let currentDisplayUpdateCallback = null; // 显示更新回调函数

/**
 * 初始化学习时长跟踪
 * @param {Function} recordCallback - 记录学习时长的回调函数
 * @param {Function} displayUpdateCallback - 显示更新回调函数（可选，用于实时显示）
 */
export function initStudyTimeTracker(recordCallback, displayUpdateCallback = null) {
  if (!recordCallback) {
    console.warn('学习时长跟踪：未提供记录回调函数');
    return;
  }

  // 保存回调函数
  currentRecordCallback = recordCallback;
  currentDisplayUpdateCallback = displayUpdateCallback;

  // 记录页面进入时间
  pageEnterTime = Date.now();
  lastRecordTime = Date.now();
  accumulatedTime = 0;

  // 监听页面可见性变化
  document.addEventListener('visibilitychange', handleVisibilityChange);

  // 监听页面卸载
  window.addEventListener('beforeunload', handleBeforeUnload);

  // 启动定时记录
  startTracking();
  
  // 启动实时显示更新
  startDisplayUpdate();

  console.log('学习时长跟踪已启动');
}

/**
 * 处理页面可见性变化
 */
function handleVisibilityChange() {
  if (document.hidden) {
    // 页面隐藏，停止跟踪
    isPageVisible = false;
    if (trackingTimer) {
      clearInterval(trackingTimer);
      trackingTimer = null;
    }
    if (displayTimer) {
      clearInterval(displayTimer);
      displayTimer = null;
    }
    // 保存已累计的时间
    if (lastRecordTime) {
      const timeSpent = Date.now() - lastRecordTime;
      accumulatedTime += timeSpent;
      lastRecordTime = null;
    }
  } else {
    // 页面显示，恢复跟踪
    isPageVisible = true;
    lastRecordTime = Date.now();
    // 重新启动定时跟踪
    if (currentRecordCallback) {
      startTracking();
      startDisplayUpdate();
    }
  }
}

/**
 * 处理页面卸载
 */
function handleBeforeUnload() {
  saveAccumulatedTime();
}

/**
 * 启动定时跟踪
 */
function startTracking() {
  if (!currentRecordCallback) {
    console.warn('学习时长跟踪：未提供记录回调函数');
    return;
  }

  // 清除旧的定时器
  if (trackingTimer) {
    clearInterval(trackingTimer);
  }

  // 设置定时器，每30秒检查一次（根据TRACKING_INTERVAL配置）
  trackingTimer = setInterval(() => {
    if (isPageVisible && lastRecordTime && currentRecordCallback) {
      const timeSpent = Date.now() - lastRecordTime;
      const totalTime = accumulatedTime + timeSpent;
      const hours = totalTime / (60 * 60 * 1000); // 转换为小时
      const minHours = MIN_STUDY_TIME;
      
      console.log(`[学习时长跟踪] 检查: 累计=${hours.toFixed(4)}小时, 最小=${minHours}小时, 页面可见=${isPageVisible}`);
      
      // 如果累计时间超过最小记录时长，记录学习时长
      if (totalTime >= MIN_STUDY_TIME * 60 * 60 * 1000) {
        console.log(`[学习时长跟踪] 达到最小记录时长，开始记录: ${hours.toFixed(4)}小时`);
        currentRecordCallback(hours).then(() => {
          console.log(`[学习时长跟踪] 记录成功: ${hours.toFixed(4)}小时`);
        }).catch(err => {
          console.error('[学习时长跟踪] 自动记录学习时长失败:', err);
        });
        
        // 重置累计时间
        accumulatedTime = 0;
        lastRecordTime = Date.now();
      } else {
        // 累计时间不足，继续累计
        console.log(`[学习时长跟踪] 累计时间不足，继续累计: ${hours.toFixed(4)}小时 < ${minHours}小时`);
        accumulatedTime = totalTime;
        lastRecordTime = Date.now();
      }
    } else {
      if (!isPageVisible) {
        console.log('[学习时长跟踪] 页面不可见，跳过检查');
      } else if (!lastRecordTime) {
        console.log('[学习时长跟踪] lastRecordTime为空，跳过检查');
      } else if (!currentRecordCallback) {
        console.log('[学习时长跟踪] currentRecordCallback为空，跳过检查');
      }
    }
  }, TRACKING_INTERVAL);
}

/**
 * 保存累计的学习时长
 */
function saveAccumulatedTime() {
  if (!lastRecordTime || !currentRecordCallback) return;

  const timeSpent = Date.now() - lastRecordTime;
  const totalTime = accumulatedTime + timeSpent;
  
  // 如果累计时间超过最小记录时长，记录学习时长
  if (totalTime >= MIN_STUDY_TIME * 60 * 60 * 1000) {
    const hours = totalTime / (60 * 60 * 1000);
    // 使用navigator.sendBeacon或同步方式记录，因为页面可能正在卸载
    try {
      // 尝试使用sendBeacon（如果支持）
      if (navigator.sendBeacon) {
        const data = JSON.stringify({ study_hours: hours });
        const blob = new Blob([data], { type: 'application/json' });
        // 注意：sendBeacon需要完整的URL，这里先尝试同步调用
        // 如果失败，会在控制台记录错误
        currentRecordCallback(hours).catch(err => {
          console.error('保存学习时长失败:', err);
        });
      } else {
        // 降级方案：直接调用（可能失败，但不影响用户体验）
        currentRecordCallback(hours).catch(err => {
          console.error('保存学习时长失败:', err);
        });
      }
    } catch (err) {
      console.error('保存学习时长失败:', err);
    }
  } else if (totalTime > 0) {
    // 即使累计时间不足最小记录时长，也尝试保存（但只保存大于0的时间）
    // 这样可以避免丢失学习时长数据
    const hours = totalTime / (60 * 60 * 1000);
    if (hours > 0.001) { // 至少0.001小时（约3.6秒）才保存
      try {
        currentRecordCallback(hours).catch(err => {
          console.warn('保存少量学习时长失败（可忽略）:', err);
        });
      } catch (err) {
        console.warn('保存少量学习时长失败（可忽略）:', err);
      }
    }
  }
}

/**
 * 启动实时显示更新
 */
function startDisplayUpdate() {
  if (!currentDisplayUpdateCallback) return;

  // 清除旧的显示定时器
  if (displayTimer) {
    clearInterval(displayTimer);
  }

  // 设置定时器，每5秒更新一次显示
  displayTimer = setInterval(() => {
    if (isPageVisible && lastRecordTime && currentDisplayUpdateCallback) {
      const timeSpent = Date.now() - lastRecordTime;
      const totalTime = accumulatedTime + timeSpent;
      const hours = totalTime / (60 * 60 * 1000); // 转换为小时
      
      // 调用显示更新回调
      try {
        currentDisplayUpdateCallback(hours);
      } catch (err) {
        console.error('更新显示失败:', err);
      }
    }
  }, DISPLAY_UPDATE_INTERVAL);
}

/**
 * 获取当前累计的学习时长（小时）
 */
export function getCurrentAccumulatedTime() {
  if (!lastRecordTime) return 0;
  const timeSpent = Date.now() - lastRecordTime;
  const totalTime = accumulatedTime + timeSpent;
  return totalTime / (60 * 60 * 1000); // 转换为小时
}

/**
 * 清理学习时长跟踪
 */
export function cleanupStudyTimeTracker() {
  // 先保存累计的学习时长
  if (currentRecordCallback) {
    saveAccumulatedTime();
  }

  // 清除定时器
  if (trackingTimer) {
    clearInterval(trackingTimer);
    trackingTimer = null;
  }
  if (displayTimer) {
    clearInterval(displayTimer);
    displayTimer = null;
  }

  // 移除事件监听
  document.removeEventListener('visibilitychange', handleVisibilityChange);
  window.removeEventListener('beforeunload', handleBeforeUnload);

  // 重置状态
  pageEnterTime = null;
  lastRecordTime = null;
  accumulatedTime = 0;
  isPageVisible = true;
  currentRecordCallback = null;
  currentDisplayUpdateCallback = null;

  console.log('学习时长跟踪已清理');
}

/**
 * 记录学习阶段完成时的学习时长
 * @param {Function} recordCallback - 记录学习时长的回调函数
 * @param {number} hours - 学习时长（小时），默认使用配置的奖励时长
 */
export async function recordStageCompletionTime(recordCallback, hours = STAGE_COMPLETION_REWARD) {
  if (!recordCallback) {
    console.warn('学习时长跟踪：未提供记录回调函数');
    return;
  }

  try {
    await recordCallback(hours);
    console.log(`已记录学习阶段完成时长: ${hours}小时`);
  } catch (err) {
    console.error('记录学习阶段完成时长失败:', err);
  }
}

/**
 * 获取页面停留时间（小时）
 */
export function getPageStayTime() {
  if (!pageEnterTime) return 0;
  return (Date.now() - pageEnterTime) / (60 * 60 * 1000);
}

