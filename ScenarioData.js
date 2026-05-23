var ScenarioData = {
	rawData: "",
	rawErrors: "",
	lessonNames: {
    "KT_Nguon_MD": "Kiểm tra khả năng hoạt động của các hệ thống bằng nguồn điện mặt đất",
    "KT_Nguon_AQ": "Kiểm tra khả năng hoạt động của các hệ thống bằng nguồn điện Ắc quy",
    "KT_Truoc_KD": "Kiểm tra khả năng hoạt động của các hệ thống trước khi khởi động",
    "KD_DC": "Khởi động động cơ"
},

	initData: function() {
		this.rawData += "KT_Nguon_MD | nguonNangLuong.congTacNguon.akum_lev.1.1 | Tôi đã sửa | nan\n";
		this.rawData += "KT_Nguon_MD | nguonNangLuong.congTacNguon.akum_prav.1.2 | Kiểm tra khả năng hoạt động của các hệ thống trên máy bay khi sử dụng nguồn điện sân bay: | Выполнить проверку работоспособности бортовых систем при питании от аэродромного источника энергии:\n";
		this.rawData += "KT_Nguon_MD | nguonNangLuong.congTacNguon.generator_prav.1.4 | Bật công tắc АККУМ ЛЕВ (ẮC QUY TRÁI); | включить выключатель АККУМ ЛЕВ;\n";
		this.rawData += "KT_Nguon_MD | nguonNangLuong.congTacNguon.generator_vcy.1.5 | Bật công tắc АККУМ ПРАВ (ẮC QUY PHẢI); | включить выключатель АККУМ ПРАВ;\n";
		this.rawData += "KT_Nguon_MD | nguonNangLuong.congTacNguon.topl_nasos.1.6 | Kiểm tra hiển thị trên МФЦИ (Màn hình chỉ thị đa năng) của cả hai buồng lái | проконтролировать индикацию на МФЦИ обеих кабин мнемокадров:\n";
		this.rawData += "KT_Nguon_MD | nguonNangLuong.congTacNguon.kislorod_oxy.1.7 | Trên màn hình bên trái hiển thị khung hình Kiểm tra trước khi bay ПРЕДПОЛЕТНЫЙ КОНТРОЛЬ; | на левом ПРЕДПОЛЕТНЫЙ КОНТРОЛЬ;\n";
		this.rawData += "KT_Nguon_MD | btn_next.1.8 | Trên màn hình bên phải hiển thị khung hình КИСС ТИПОВОЙ; | на правом КИСС ТИПОВОЙ;\n";
		this.rawData += "KT_Nguon_MD | btn_next.1.9 | Trên màn hình ở giữa hiển thị khung hình КИСС СЭС; | на среднем КИСС СЭС;\n";
		this.rawData += "KT_Nguon_MD | btn_next.1.10 | Kiểm tra liên lạc vô tuyến qua thiết bị liên lạc nội bộ СПУ giữa các phi công ở buồng lái trước và buồng lái sau, với kỹ thuật trưởng máy bay và điều chỉnh âm lượng nếu cần thiết; | проверить радиосвязь по СПУ между летчиками в первой и второй кабинах, с техником самолета и при необходимости отрегулировать громкость;\n";
		this.rawData += "KT_Nguon_MD | btn_next.1.11 | Kiểm tra việc thiết lập kênh liên lạc vô tuyến với chỉ huy bay trên bảng điều khiển của СПУ; | проверить установку канала радиосвязи с руководителем полетов на объединенном пульте управления СПУ;\n";
		this.rawData += "KT_Nguon_MD | btn_yes.1.1 | Thực hiện tuần tự các hướng dẫn hiển thị trong cửa sổ 5 của khung hình ПРЕДПОЛЕТНЫЙ КОНТРОЛЬ: | выполнить последовательно инструкции, предъявляемые в окне 5 мнемокадра ПРЕДПОЛЕТНЫЙ КОНТРОЛЬ:\n";
		this.rawData += "KT_Nguon_MD | btn_next.2.1 | Chỉ dẫn 1: ЗАПРИ ФОНАРЬ (ĐÓNG NẮP BUỒNG LÁI) | 1. ЗАПРИ ФОНАРЬ\n";
		this.rawData += "KT_Nguon_MD | btn_next.2.2 | - Ra lệnh cho kỹ thuật viên máy bay đóng nắp buồng lái. Sau khi đóng nắp buồng lái, hãy kiểm tra: | дать команду технику самолета на закрытие фонаря. После закрытия фонаря проконтролировать:\n";
		this.rawData += "KT_Nguon_MD | btn_next.2.3 | - Tay nắm mở nắp buồng lái ОТКРЫТИЕ ФОНАРЯ được đặt ở vị trí đóng ФОНАРЬ ЗАКРЫТ và đã được chốt; | ручка ОТКРЫТИЕ ФОНАРЯ установлена в положение ФОНАРЬ ЗАКРЫТ и застопорена;\n";
		this.rawData += "KT_Nguon_MD | btn_next.2.4 | - Chỉ báo cơ học, ở bảng đứng bên trái, khớp với vạch ФОНАРЬ ЗАКРЫТ (NẮP ĐÓNG); | механический указатель, на левом вертикальном борту, совмещен с риской ФОНАРЬ ЗАКРЫТ;\n";
		this.rawData += "KT_Nguon_MD | btn_next.2.5 | - Đèn chỉ báo trạng thái mở nắp buồng lái trên khung hình КИСС ТИПОВОЙ tắt; | погасание индикатора открытого положения фонаря на мнемокадре КИСС ТИПОВОЙ;\n";
		this.rawData += "KT_Nguon_MD | btn_yes.2.1 | - Thông báo ЗАПРИ ФОНАР tắt. | погасание инструкции ЗАПРИ ФОНАРЬ.\n";
		this.rawData += "KT_Nguon_MD | btn_next.3.1 | - Nếu kêt quả kiểm tra tốt hãy nhấn nút ДА để đi tiếp, nếu không tốt hãy nhấn nút НЕТ. | Подтверждение результата проверки каждой последующей инструкции выполняется из одной или двух кабин (в зависимости от количества членов экипажа) нажатием кнопки ДА или НЕТ на мнемокадре ПРЕДПОЛЕТНЫЙ КОНТРОЛЬ.\n";
		this.rawData += "KT_Nguon_MD | btn_next.3.2 | Lưu ý: Cho phép đóng nắp buồng lái ngay trước khi khởi động động cơ, khi đó thông báo ЗАПРИ ФОНАРЬ sẽ được hiển thị đồng thời với các thông báo khác khi chuẩn bị khởi động. | Примечание: Допускается закрытие фонаря непосредственно перед запуском двигателей, при этом инструкция ЗАПРИ ФОНАРЬ будет индицироваться одновременно с другими инструкциями этапа подготовки к запуску.\n";
		this.rawData += "KT_Nguon_MD | btn_yes.2.1 | Chỉ dẫn 2: ПРОВЕРЬ ЭКРАНЫ МФЦИ, УСТАНОВИ ЯРКОСТЬ (KIỂM TRA MÀN HÌNH МФЦИ, THIẾT LẬP ĐỘ SÁNG) | 2. ПРОВЕРЬ ЭКРАНЫ МФЦИ,УСТАНОВИ ЯРКОСТЬ\n";
		this.rawData += "KT_Nguon_MD | btn_next.4.2 | Kiểm tra tình trạng hoạt động của các màn hình chỉ thị bằng sự hiện diện của biểu tượng N ở góc dưới bên phải màn hình; | проконтролировать исправность индикаторов по наличию символа N в правом нижнем углу экрана;\n";
		this.rawData += "KT_Nguon_MD | btn_next.4.3 | Thiết lập độ sáng cần thiết; | установить требуемую яркость;\n";
		this.rawData += "KT_Nguon_MD | btn_yes.3.1 | Nhấn nút ДА; | нажать кнопку ДА;\n";
		this.rawData += "KT_Nguon_MD | btn_next.5.2 | Chỉ dẫn 3: ВКЛЮЧИ СТОЯНОЧНЫЙ ТОРМОЗ (BẬT PHANH ĐỖ) | 3. ВКЛЮЧИ СТОЯНОЧНЫЙ ТОРМОЗ\n";
		this.rawData += "KT_Nguon_MD | btn_next.5.3 | Dùng tay phải nắm lấy tay cầm СТОЯН ТОРМ trên thành ngang bên phải, kéo lên trên, xoay theo chiều kim đồng hồ 90 độ và cố định; | правой рукой взяться за рукоятку СТОЯН ТОРМ на правом горизонтальном пульте, потянуть ее вверх, повернуть по часовой стрелке на 90 градусов и зафиксировать;\n";
		this.rawData += "KT_Nguon_MD | btn_next.6.1 | Kiểm tra việc tắt hướng dẫn ВКЛЮЧИ СТОЯНОЧНЫЙ ТОРМОЗ và sự xuất hiện trong cửa sổ БАСК thông báo СТОЯНОЧНЫЙ ТОРМОЗ ВКЛЮЧЕН (PHANH ĐỖ ĐÃ BẬT). | проконтролировать погасание инструкции ВКЛЮЧИ СТОЯНОЧНЫЙ ТОРМОЗ и появление в окне БАСК сообщения СТОЯНОЧНЫЙ ТОРМОЗ ВКЛЮЧЕН.\n";
		this.rawData += "KT_Nguon_MD | btn_next.6.2 | Chỉ dẫn 4: ПРОВЕРЬ СЭС (KIỂM TRA HỆ THỐNG ĐIỆN) | 4. ПРОВЕРЬ СЭС\n";
		this.rawData += "KT_Nguon_MD | btn_next.6.3 | Kiểm tra điện áp nguồn điện trên khung hình КИСС СЭС | по индикации на мнемокадре СЭС проверить соответствие напряжения электропитания установленным значениям и состояние СЭС;\n";
		this.rawData += "KT_Nguon_MD | btn_next.6.4 | Nhấn nút ДА; | нажать кнопку ДА;\n";
		this.rawData += "KT_Nguon_MD | btn_next.6.5 | Kiểm tra việc thay đổi hiển thị trên màn hình МФЦИ ở giữa từ khung hình КИСС СЭС sang khung hình КИСС ДВИГАТЕЛЬ. | проконтролировать смену индикации на среднем МФЦИ мнемокадра КИСС СЭС на мнемокадр КИСС ДВИГАТЕЛЬ.\n";
		this.rawData += "KT_Nguon_MD | btn_next.6.6 | Chỉ dẫn 5: ПРОВЕРЬ РИ (KIỂM TRA THÔNG THOẠI) | 5. ПРОВЕРЬ РИ\n";
		this.rawData += "KT_Nguon_MD | btn_next.6.7 | Nhấn nút РИ trên bảng điều khiển đài vô tuyến; | нажать кнопку РИ на пульте управления радиостанцией;\n";
		this.rawData += "KT_Nguon_MD | btn_next.6.8 | Nghe thông báo РЕЧЕВОЙ ИНФОРМАТОР ИСПРАВЕН (HỆ THỐNG THÔNG THOẠI HOẠT ĐỘNG TỐT); | прослушать сообщение РЕЧЕВОЙ ИНФОРМАТОР ИСПРАВЕН;\n";
		this.rawData += "KT_Nguon_MD | btn_next.6.9 | Nhấn nút ДА. | нажать кнопку ДА.\n";
		this.rawData += "KT_Nguon_AQ | nguonNangLuong.congTacNguon.akum_lev.1.1 | Tôi đã sửa | nan\n";
		this.rawData += "KT_Nguon_AQ | nguonNangLuong.congTacNguon.akum_prav.1.2 | Khi sử dụng nguồn từ ắc quy trên máy bay, điện sẽ được cấp cho các thiết bị tiêu thụ điện cấp 1, do đó màn hình МФЦИ ở giữa trong cả hai buồng lái sẽ không hoạt động cho đến khi máy phát điện của ВСУ được kết nối vào mạng điện máy bay. | При питании от бортовых аккумуляторов электропитание подается на потребители первой категории, поэтому средний МФЦИ в обеих кабинах не работает до момента подключения генератора ВСУ к бортовой сети.\n";
		this.rawData += "KT_Nguon_AQ | nguonNangLuong.congTacNguon.generator_lev.1.3 | – Bật công tắc АККУМ ЛЕВ (ẮC QUY TRÁI); | – включить выключатель АККУМ ЛЕВ;\n";
		this.rawData += "KT_Nguon_AQ | nguonNangLuong.congTacNguon.generator_prav.1.4 | – Kiểm tra màn hình МФЦИ bên trái hiển thị khung hình  – ПРЕДПОЛЕТНЫЙ КОНТРОЛЬ (KIỂM TRA TRƯỚC KHI BAY) | – проконтролировать индикацию на МФЦИ обеих кабин мнемокадров:– на левом – ПРЕДПОЛЕТНЫЙ КОНТРОЛЬ;\n";
		this.rawData += "KT_Nguon_AQ | nguonNangLuong.congTacNguon.topl_nasos.1.6 | – Kiểm tra màn hình МФЦИ bên phải – КИСС ТИПОВОЙ; | – на правом – КИСС ТИПОВОЙ;\n";
		this.rawData += "KT_Nguon_AQ | nguonNangLuong.congTacNguon.kislorod_oxy.1.7 | – Chuyển đổi chỉ thị trên màn hình МФЦИ bên phải từ khung hình КИСС ТИПОВОЙ sang khung hình КИСС СЭС; | – переключить индикацию на правом МФЦИ с мнемокадра КИСС ТИПОВОЙ на мнемокадр КИСС СЭС;\n";
		this.rawData += "KT_Nguon_AQ | btn_next.1.8 | – Kiểm tra điện áp trong 5 giây, giá trị này phải không được nhỏ hơn 24 Vôn; | – проконтролировать в течение 5 с напряжение, которое должно быть не менее 24 В;\n";
		this.rawData += "KT_Nguon_AQ | btn_next.1.9 | – Bật công tắc АККУМ ПРАВ (ẮC QUY PHẢI); | – включить выключатель АККУМ ПРАВ;\n";
		this.rawData += "KT_Nguon_AQ | btn_next.1.10 | – Tắt công tắc АККУМ ЛЕВ (ẮC QUY TRÁI); | – отключить выключатель АККУМ ЛЕВ;\n";
		this.rawData += "KT_Nguon_AQ | btn_next.1.11 | – Kiểm tra điện áp trong 5 giây, giá trị này phải không được nhỏ hơn 24 Vôn; | – проконтролировать в течение 5 с напряжение, которое должно быть не менее 24 В;\n";
		this.rawData += "KT_Nguon_AQ | btn_yes.1.1 | – Bật công tắc АККУМ ЛЕВ (ẮC QUY TRÁI). | – включить выключатель АККУМ ЛЕВ.\n";
		this.rawData += "KT_Nguon_AQ | btn_next.2.1 | Thời gian từ lúc bật các ắc quy cho đến khi khởi động ВСУphải ở mức tối thiểu (trong cửa sổ số 3 của khung hình ПРЕДПОЛЕТНЫЙ КОНТРОЛЬ có hiển thị thang thời gian thực hiện quá trình kiểm tra trên mặt đất). | Время от момента включения аккумуляторов до запуска ВСУ должно быть минимальным (в окне 3 мнемокадра МФЦИ ПРЕДПОЛЕТНЫЙ КОНТРОЛЬ индицируется шкала времени проведения наземного контроля).\n";
		this.rawData += "KT_Nguon_AQ | btn_next.2.2 | – Thực hiện lần lượt các hướng dẫn được đưa ra trong cửa sổ số 5 của khung hình ПРЕДПОЛЕТНЫЙ КОНТРОЛЬ, tương tự như quy trình kiểm tra khi được cấp điện từ nguồn điện sân bay. | – выполнить последовательно инструкции, предъявляемые в окне 5 мнемокадра ПРЕДПОЛЕТНЫЙ КОНТРОЛЬ, аналогично проверке при наличии питания от аэродромного источника энергии\n";
		this.rawData += "KT_Truoc_KD | nguonNangLuong.congTacNguon.akum_lev.1.1 | 1. kiểm tra khả năng hoạt động của các hệ thống trên máy bay trước khi khởi động động cơ | 1. Проверка работоспособности бортовых систем перед запуском двигателей\n";
		this.rawData += "KT_Truoc_KD | nguonNangLuong.congTacNguon.akum_prav.1.2 | Sau khi thực hiện quy trình kiểm tra các hệ thống trên máy bay từ các nguồn điện, trong cửa sổ số 5 của khung hình ПРЕДПОЛЕТНЫЙ КОНТРОЛЬ sẽ lần lượt đưa ra các hướng dẫn sau: | После выполнения процедуры проверки бортовых систем от источников электропитания в окне 5 мнемокадра ПРЕДПОЛЕТНЫЙ КОНТРОЛЬ последовательно выводятся следующие инструкции:\n";
		this.rawData += "KT_Truoc_KD | nguonNangLuong.congTacNguon.generator_lev.1.3 | 1.    ПРОВЕРЬ ВНУТРИКАБИННОЕ ОСВЕЩЕНИЕ (KIỂM TRA CHIẾU SÁNG TRONG BUỒNG LÁI) | 1. ПРОВЕРЬВНУТРИКАБИННОЕ ОСВЕЩЕНИЕ\n";
		this.rawData += "KT_Truoc_KD | nguonNangLuong.congTacNguon.generator_prav.1.4 | – Thực hiện kiểm tra bằng mắt thường hệ thống chiếu sáng trong buồng lái; | – выполнить визуальную проверку внутрикабинного освещения;\n";
		this.rawData += "KT_Truoc_KD | nguonNangLuong.congTacNguon.generator_vcy.1.5 | – Nhấn nút ДА. | – нажать кнопку ДА.\n";
		this.rawData += "KT_Truoc_KD | nguonNangLuong.congTacNguon.topl_nasos.1.6 | 2.    ПРОВЕРЬ ИНДИКАТОР ПУИ (KIỂM TRA MÀN HÌNH CHỈ THỊ PUI) | 2. ПРОВЕРЬИНДИКАТОР ПУИ\n";
		this.rawData += "KT_Truoc_KD | nguonNangLuong.congTacNguon.kislorod_oxy.1.7 | – Kiểm tra để đảm bảo trên ПУИ không có thông báo НЕТ ИНФОРМАЦИИ (KHÔNG CÓ THÔNG TIN); | – проконтролировать отсутствие на ПУИ сообщения НЕТ ИНФОРМАЦИИ;\n";
		this.rawData += "KD_DC | nguonNangLuong.congTacNguon.akum_lev.1.1 | 1. Khởi động tự động ВСУ và hai động cơ (phương pháp khởi động chính khi có nguồn điện từ sân bay) | 1. Автоматический запуск ВСУ и двух двигателей (основной способ запуска при наличии аэродромного источника энергии)\n";
		this.rawData += "KD_DC | nguonNangLuong.congTacNguon.akum_prav.1.2 | 1.    Sau khi nhận được sự cho phép khởi động, lần lượt bật các công tắc: | 1. Получив разрешение на запуск включить выключатели на правом вертикальном борту:\n";
		this.rawData += "KD_DC | nguonNangLuong.congTacNguon.generator_lev.1.3 | – ГЕНЕРАТОР ЛЕВ (MÁY PHÁT ĐIỆN TRÁI); | ‒ ГЕНЕРАТОР ЛЕВ;\n";
		this.rawData += "KD_DC | nguonNangLuong.congTacNguon.generator_prav.1.4 | – ГЕНЕРАТОР ПРАВ (MÁY PHÁT ĐIỆN PHẢI); | ‒ ГЕНЕРАТОР ПРАВ;\n";
		this.rawData += "KD_DC | nguonNangLuong.congTacNguon.generator_vcy.1.5 | – ТОПЛ НАСОСЫ (BƠM NHIÊN LIỆU); | ‒ ТОПЛ НАСОСЫ;\n";
		this.rawData += "KD_DC | nguonNangLuong.congTacNguon.topl_nasos.1.6 | – КИСЛОРОД (OXY). | ‒ КИСЛОРОД.\n";
		this.rawData += "KD_DC | nguonNangLuong.congTacNguon.kislorod_oxy.1.7 | 2. Đưa РУД (tay dầu) của cả hai động cơ vào vị trí МГ (Ga nhỏ). | 2. Установить РУД обоих двигателей на упор МГ.\n";

		this.rawErrors += "Thao tác sai, vui lòng thử lại. | Неверное действие, попробуйте снова.\n";
		this.rawErrors += "Bạn đã ấn nhầm nút, hãy kiểm tra kỹ. | Вы нажали не ту кнопку, проверьте еще раз.\n";
		this.rawErrors += "Chưa đúng, hãy nhìn vào vòng tròn gợi ý. | Ошибка! Обратите внимание на подсказку.\n";
	}
};
ScenarioData.initData(); // Tự động khởi tạo khi load file
