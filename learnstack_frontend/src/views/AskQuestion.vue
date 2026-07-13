<template>
  <div class="ask-question">
    <div class="container">
      <div class="page-header">
        <h1>发布帖子</h1>
        <p>请详细描述您的帖子内容，以便获得更好的回答</p>
      </div>

      <div class="question-form">
        <form @submit.prevent="handleSubmit">
          <!-- 帖子标题 -->
          <div class="form-group">
            <label for="title" class="form-label">帖子标题 <span class="required">*</span></label>
            <input
              type="text"
              id="title"
              v-model="formData.title"
              class="form-input"
              placeholder="请输入帖子标题（5-20字）"
              maxlength="20"
              required
            >
            <div class="char-count">{{ formData.title.length }}/20</div>
          </div>

          <!-- 帖子描述 -->
          <div class="form-group">
            <label for="description" class="form-label">帖子描述 <span class="required">*</span></label>
            <textarea
              id="description"
              v-model="formData.description"
              class="form-textarea"
              placeholder="请简要描述您的帖子内容（10-200字）"
              rows="2"
              maxlength="200"
              required
            ></textarea>
            <div class="char-count">{{ formData.description.length }}/200</div>
          </div>
          
          <!-- 帖子内容 -->
          <div class="form-group">
            <label for="content" class="form-label">详细内容 <span class="required">*</span></label>
            <textarea
              id="content"
              v-model="formData.content"
              class="form-textarea"
              placeholder="请详细描述您的帖子内容，包括相关背景、您已经尝试过的方法等（30-1000字）"
              rows="10"
              maxlength="1000"
              required
            ></textarea>
            <div class="char-count">{{ formData.content.length }}/1000</div>
          </div>

          <!-- 帖子分类（将作为标签使用） -->
          <div class="form-group">
            <label for="category" class="form-label">技术分类 <span class="required">*</span></label>
            <input
              type="text"
              id="category"
              v-model="formData.category"
              class="form-input"
              placeholder="请输入分类名称（例如：前端开发、Python、机器学习等）"
              maxlength="50"
              required
            >
            <div class="char-count">{{ formData.category.length }}/50</div>
            <p class="form-hint">此分类将自动添加到标签中</p>
          </div>

          <!-- 标签输入 -->
          <div class="form-group">
            <label class="form-label">标签</label>
            <div class="tags-input-container">
              <input
                type="text"
                v-model="tagInput"
                class="form-input tag-input"
                placeholder="输入标签名称"
                maxlength="20"
                @keyup.enter="addTag"
              >
              <button type="button" class="add-tag-btn" @click="addTag" :disabled="!tagInput.trim() || tags.length >= 5">
                添加标签
              </button>
            </div>
            <!-- 已添加的标签 -->
            <div class="tags-list" v-if="tags.length > 0">
              <span v-for="(tag, index) in tags" :key="index" class="tag-item">
                {{ tag }}
                <button type="button" class="remove-tag-btn" @click="removeTag(index)">×</button>
              </span>
            </div>
            <p class="form-hint">最多添加5个标签，每个标签不超过20个字符</p>
          </div>



          <!-- 提交按钮 -->
          <div class="form-actions">
            <button type="button" @click="goBack" class="cancel-btn">取消</button>
            <button type="submit" class="submit-btn" :disabled="loading">
              <i v-if="loading" class="fas fa-spinner fa-spin"></i>
              {{ loading ? '发布中...' : '发布帖子' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import communityService from '../services/communityService';

export default {
  name: 'AskQuestion',
  setup() {
    const router = useRouter();
    const route = useRoute();
    const loading = ref(false);
    const error = ref('');

    // 表单数据
    const formData = reactive({
      title: '',
      description: '',
      content: '',
      category: ''
    });
    
    // 标签相关
    const tagInput = ref('');
    const tags = ref([]);

    // 添加标签
    const addTag = () => {
      const newTag = tagInput.value.trim();
      
      if (!newTag) {
        alert('请输入标签内容');
        return;
      }
      
      if (newTag.length > 20) {
        alert('标签长度不能超过20个字符');
        return;
      }
      
      if (tags.value.length >= 5) {
        alert('最多只能添加5个标签');
        return;
      }
      
      if (tags.value.includes(newTag)) {
        alert('该标签已存在');
        return;
      }
      
      tags.value.push(newTag);
      tagInput.value = '';
    };
    
    // 删除标签
    const removeTag = (index) => {
      tags.value.splice(index, 1);
    };

    // 处理表单提交
    const handleSubmit = async () => {
      // 基本验证
      if (formData.title.length < 5 || formData.title.length > 20) {
        alert('标题长度必须在5-20个字符之间');
        return;
      }
      
      if (formData.description.length < 10 || formData.description.length > 200) {
        alert('帖子描述长度必须在10-200个字符之间');
        return;
      }
      
      if (formData.content.length < 30 || formData.content.length > 1000) {
        alert('详细内容长度必须在30-1000个字符之间');
        return;
      }

      loading.value = true;
      error.value = '';

      try {
        // 准备标签数据：如果用户输入了标签，则使用标签；否则使用分类作为标签
        let finalTags = '';
        if (tags.value.length > 0) {
          // 用户输入了标签，使用用户输入的标签
          finalTags = tags.value.join(',');
        } else if (formData.category.trim()) {
          // 用户没有输入标签，但输入了分类，将分类作为标签
          finalTags = formData.category.trim();
        }
        
        // 移除emoji和特殊字符的函数
        const removeEmoji = (text) => {
          return text
            .replace(/[\u{1F300}-\u{1F9FF}]/gu, '')
            .replace(/[\u{1F600}-\u{1F64F}]/gu, '')
            .replace(/[\u{1F680}-\u{1F6FF}]/gu, '')
            .replace(/[\u{2600}-\u{26FF}]/gu, '')
            .replace(/[\u{2700}-\u{27BF}]/gu, '');
        };
        
        // 准备提交数据，移除emoji字符以避免数据库错误
        const submitData = {
          title: removeEmoji(formData.title.trim()),
          description: removeEmoji(formData.description.trim()),
          content: removeEmoji(formData.content.trim()),
          tags: finalTags.length > 200 ? finalTags.substring(0, 200) : finalTags // 标签限制在200字符以内
        };

        // 调用API创建帖子
        const response = await communityService.createQuestion(submitData);
        
        // 提交成功后跳转到帖子详情页
        alert('帖子发布成功！');
        router.push(`/community/${response.id}`);
      } catch (err) {
        console.error('发布帖子失败:', err);
        error.value = '发布帖子失败，请稍后重试';
        alert('发布失败：' + (err.response?.data?.detail || '未知错误'));
      } finally {
        loading.value = false;
      }
    };

    // 移除emoji和特殊字符的函数
    const removeEmojiAndSpecialChars = (text) => {
      if (!text) return text;
      // 移除emoji和4字节UTF-8字符（如emoji）
      return text
        .replace(/[\u{1F300}-\u{1F9FF}]/gu, '') // emoji范围1
        .replace(/[\u{1F600}-\u{1F64F}]/gu, '') // emoji范围2  
        .replace(/[\u{1F680}-\u{1F6FF}]/gu, '') // emoji范围3
        .replace(/[\u{2600}-\u{26FF}]/gu, '') // 其他符号
        .replace(/[\u{2700}-\u{27BF}]/gu, ''); // 装饰符号
    };
    
    // 处理URL中的context参数
    const processContextParam = () => {
      try {
        const context = route.query.context;
        if (context) {
          // 解码URL编码的上下文内容
          let decodedContext = decodeURIComponent(context);
          
          // 移除emoji和特殊字符，避免数据库存储错误
          decodedContext = removeEmojiAndSpecialChars(decodedContext);
          
          // 如果context太长，截取前1000个字符（匹配content的最大长度）
          const maxLength = 1000;
          formData.content = decodedContext.length > maxLength 
            ? decodedContext.substring(0, maxLength) 
            : decodedContext;
          
          // 尝试从上下文提取简短描述作为帖子描述
          const lines = decodedContext.split('\n');
          if (lines.length > 0) {
            // 取第一行作为描述，但限制在200字符以内
            formData.description = lines[0].substring(0, 200);
          }
          
          // 如果有提示，告知用户内容已被截取
          if (decodedContext.length > maxLength) {
            alert('提示：来自AI助手的上下文内容较长，部分内容已被截取。您可以在发布前手动编辑。');
          }
        }
      } catch (err) {
        console.error('处理上下文参数失败:', err);
      }
    };
    
    // 组件挂载时处理参数
    onMounted(() => {
      processContextParam();
    });
    
    // 返回上一页
    const goBack = () => {
      router.back();
    };

    return {
      loading,
      error,
      formData,
      tagInput,
      tags,
      addTag,
      removeTag,
      handleSubmit,
      goBack
    };
  }
};
</script>

<style scoped>
.ask-question {
  padding: 2rem 0;
  background-color: #f8f9fa;
  min-height: calc(100vh - 120px);
}

.container {
  max-width: 800px;
  margin: 0 auto;
  padding: 0 1rem;
}

.page-header {
  text-align: center;
  margin-bottom: 2rem;
}

.page-header h1 {
  font-size: 2.2rem;
  color: #333;
  margin-bottom: 0.5rem;
}

.page-header p {
  font-size: 1.1rem;
  color: #666;
}

.question-form {
  background: white;
  border-radius: 8px;
  padding: 2rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.form-group {
  margin-bottom: 1.5rem;
  position: relative;
}

.form-label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #333;
  font-size: 1rem;
}

.required {
  color: #e74c3c;
}

.form-input,
.form-textarea,
.form-select {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
  transition: border-color 0.3s;
  box-sizing: border-box;
}

.form-input:focus,
.form-textarea:focus,
.form-select:focus {
  outline: none;
  border-color: #646cff;
  box-shadow: 0 0 0 2px rgba(100, 108, 255, 0.2);
}

.form-textarea {
  resize: vertical;
  min-height: 100px;
}

.char-count {
  text-align: right;
  font-size: 0.85rem;
  color: #666;
  margin-top: 0.25rem;
}

.form-hint {
  font-size: 0.85rem;
  color: #666;
  margin-top: 0.25rem;
  margin-bottom: 0;
}

.checkbox-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.form-checkbox {
  width: auto;
  margin: 0;
}

.checkbox-label {
  font-weight: normal;
  cursor: pointer;
  user-select: none;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 2rem;
}

.cancel-btn {
  padding: 0.75rem 1.5rem;
  background: #f8f9fa;
  color: #666;
  border: 1px solid #ddd;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  transition: all 0.3s;
}

.cancel-btn:hover {
  background: #e9ecef;
}

.submit-btn {
  padding: 0.75rem 2rem;
  background: #2563eb;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 1rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  transition: background 0.3s;
}

.submit-btn:hover:not(:disabled) {
  background: #2625ebff;
}

.submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .question-form {
    padding: 1.5rem;
  }
  
  .form-actions {
    flex-direction: column;
  }
  
  .cancel-btn,
  .submit-btn {
    width: 100%;
  }
  
  .tags-input-container {
    flex-direction: column;
  }
  
  .add-tag-btn {
    width: 100%;
  }
}

/* 标签输入样式 */
.tags-input-container {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
}

.tag-input {
  flex: 1;
}

.add-tag-btn {
  padding: 0.5rem 1rem;
  background-color: #2563eb;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 0.9rem;
}

.add-tag-btn:hover:not(:disabled) {
  background-color: #2625ebff;
}

.add-tag-btn:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.tags-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}

.tag-item {
      display: inline-flex;
      align-items: center;
      background-color: #f0f0f0;
      color: #333;
      padding: 0.25rem 0.75rem;
      border-radius: 2px;
      font-size: 0.9rem;
    }

.remove-tag-btn {
      background: none;
      border: none;
      color: #666;
      margin-left: 0.5rem;
      cursor: pointer;
      font-size: 1rem;
      line-height: 1;
      padding: 0;
      width: 16px;
      height: 16px;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    
    .remove-tag-btn:hover {
      color: #d32f2f;
    }
</style>