import streamlit as st
import streamlit.components.v1 as components

# 1. 화면 기본 설정
st.set_page_config(page_title="7C 무한 비행", page_icon="✈️", layout="centered")

st.title("✈️ 7C 무한 비행: 먹구름을 피해라!")
st.markdown("스마트폰에서는 **비행기를 손가락으로 꾹 누른 채 요리조리 드래그**해서 번개 구름을 피하세요!")
st.markdown("---")

# 2. 게임 그래픽 및 액션을 위한 HTML/JavaScript 엔진 구동
game_html = """
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
<style>
  body { display: flex; flex-direction: column; align-items: center; justify-content: center; margin: 0; touch-action: none; background-color: white;}
  canvas { background: #87CEEB; border-radius: 10px; box-shadow: 0 4px 8px rgba(0,0,0,0.2); }
  #score { font-size: 24px; font-family: 'Arial', sans-serif; font-weight: bold; margin-bottom: 10px; color: #333; }
  #game-over { color: red; font-size: 22px; font-weight: bold; display: none; margin-top: 10px; text-align: center; }
  #btn-restart { margin-top: 15px; padding: 10px 20px; font-size: 18px; cursor: pointer; background: #FF4B4B; color: white; border: none; border-radius: 5px; display: none; font-weight: bold; }
</style>
</head>
<body>
  <div id="score">비행 거리: 0 km</div>
  <canvas id="gameCanvas" width="350" height="450"></canvas>
  <div id="game-over">💥 앗! 난기류(먹구름)에 휘말렸습니다!</div>
  <button id="btn-restart" onclick="resetGame()">🔄 다시 비행하기</button>

<script>
  const canvas = document.getElementById("gameCanvas");
  const ctx = canvas.getContext("2d");
  let score = 0;
  let gameOver = false;
  let animationId;

  // 플레이어 (비행기)
  const player = { x: 155, y: 380, width: 40, height: 40, emoji: "✈️" };

  // 장애물 (먹구름)
  let obstacles = [];
  let obstacleSpeed = 4; // 구름 떨어지는 속도

  function drawPlayer() {
      ctx.font = "40px Arial";
      ctx.fillText(player.emoji, player.x, player.y + 35);
  }

  function drawObstacles() {
      ctx.font = "40px Arial";
      for (let i = 0; i < obstacles.length; i++) {
          ctx.fillText("🌩️", obstacles[i].x, obstacles[i].y + 35);
      }
  }

  function updateObstacles() {
      for (let i = 0; i < obstacles.length; i++) {
          obstacles[i].y += obstacleSpeed;
          
          // 충돌 감지 로직 (비행기와 구름이 닿았는가?)
          if (player.x < obstacles[i].x + 30 &&
              player.x + 30 > obstacles[i].x &&
              player.y < obstacles[i].y + 30 &&
              player.y + 30 > obstacles[i].y) {
              gameOver = true;
          }
      }

      // 화면 아래로 지나간 구름 없애기 + 점수 올리기
      if (obstacles.length > 0 && obstacles[0].y > canvas.height) {
          obstacles.shift();
          score += 10;
          document.getElementById("score").innerText = "비행 거리: " + score + " km";
          // 50km마다 구름 속도가 빨라져서 난이도 상승!
          if (score > 0 && score % 50 === 0) obstacleSpeed += 0.5; 
      }

      // 새로운 먹구름 무작위 생성
      if (Math.random() < 0.06) {
          obstacles.push({ x: Math.random() * (canvas.width - 40), y: -40 });
      }
  }

  function gameLoop() {
      if (gameOver) {
          document.getElementById("game-over").style.display = "block";
          document.getElementById("btn-restart").style.display = "block";
          return;
      }

      ctx.clearRect(0, 0, canvas.width, canvas.height);
      drawPlayer();
      updateObstacles();
      drawObstacles();

      animationId = requestAnimationFrame(gameLoop);
  }

  // 모바일 터치(드래그) 조작
  canvas.addEventListener("touchmove", function(e) {
      e.preventDefault();
      let rect = canvas.getBoundingClientRect();
      let touch = e.touches[0];
      player.x = touch.clientX - rect.left - player.width / 2;
      player.y = touch.clientY - rect.top - player.height / 2;
      
      // 화면 밖으로 못 나가게 막기
      if (player.x < 0) player.x = 0;
      if (player.x + player.width > canvas.width) player.x = canvas.width - player.width;
      if (player.y < 0) player.y = 0;
      if (player.y + player.height > canvas.height) player.y = canvas.height - player.height;
  }, { passive: false });

  // PC 마우스 조작 (테스트용)
  canvas.addEventListener("mousemove", function(e) {
      let rect = canvas.getBoundingClientRect();
      player.x = e.clientX - rect.left - player.width / 2;
      player.y = e.clientY - rect.top - player.height / 2;
      if (player.x < 0) player.x = 0;
      if (player.x + player.width > canvas.width) player.x = canvas.width - player.width;
      if (player.y < 0) player.y = 0;
      if (player.y + player.height > canvas.height) player.y = canvas.height - player.height;
  });

  function resetGame() {
      score = 0;
      gameOver = false;
      obstacles = [];
      obstacleSpeed = 4;
      player.x = 155;
      player.y = 380;
      document.getElementById("score").innerText = "비행 거리: 0 km";
      document.getElementById("game-over").style.display = "none";
      document.getElementById("btn-restart").style.display = "none";
      gameLoop();
  }

  resetGame(); // 게임 시작
</script>
</body>
</html>
"""

# 웹 화면에 게임 엔진 이식
components.html(game_html, height=600)
