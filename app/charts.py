# !/usr/bin/env python3
# -*- coding: utf-8 -*-

# made by Jirrik

"""Functions that generate HTML pages."""

from app.init import val

class Webpages():

    @staticmethod
    def build_chart(exchange, pair):
        tradingview = '<script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>'
        tradingview += '<script type="text/javascript">'
        tradingview += 'new TradingView.widget({'
        tradingview += '  "autosize": true,'
        # tradingview += '  "symbol": "BINANCE:BNBBTC",'
        tradingview += '  "symbol": "' + exchange + ':' + pair + '",'
        tradingview += '  "interval": "60",'
        tradingview += '  "timezone": "Etc/UTC",'
        tradingview += '  "theme": "Dark",'
        tradingview += '  "style": "1",'
        tradingview += '  "locale": "en",'
        tradingview += '  "toolbar_bg": "#f1f3f6",'
        tradingview += '  "enable_publishing": false,'
        tradingview += '  "hide_side_toolbar": false,'
        tradingview += '  "allow_symbol_change": true,'
        tradingview += '  "hideideas": true,'
        tradingview += '  "studies": ['
        tradingview += '    "StochasticRSI@tv-basicstudies",'
        tradingview += '    "BB@tv-basicstudies"'
        tradingview += '  ]'
        tradingview += '});'
        tradingview += '</script>'

        return tradingview

    @staticmethod
    def build_chart2(pair, timeframe):
        chart = """
    <!-- TradingView Widget BEGIN -->
    <style>
        * {background: black;}
      html,
      body
      {
        background: #000 none repeat scroll 0 0;
        color: #333;
        font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
      }

      a:hover
      {
        color: #58c3e5;
      }

      .chart-page .chart-container
      {
        background-color: #222;
        border-color: #444;
      }

      .header-chart-panel
      {
        background-color: #222;
      }

      .tv-side-toolbar
      {
        background-color: #222;
        border-color: #444;
        color: #999;
      }

      .tv-side-toolbar .tools-group:not(:first-child):not(.no-delimiter)::before
      {
        background-color: #444;
      }

        .tv-side-toolbar .tools-group .button:active:not(.subgroup),
      .tv-side-toolbar .tools-group .button.active:not(.subgroup),
      .tv-side-toolbar .tools-group .button.selected:not(.subgroup),
      .properties-toolbar .tools-group .button:active,
      .properties-toolbar .tools-group .button.active,
      .drawing-favorites-toolbar .tools-group .button:active,
      .drawing-favorites-toolbar .tools-group .button.active,
      .tv-side-toolbar .tools-group .button.selected .main,
      .tv-side-toolbar .tools-group .button:active .side,
      .tv-side-toolbar .tools-group .button.active .side
        {
        background-color: #444;
      }

      .tv-side-toolbar .tools-group .button .side
      {
        background-color: #444;
        border-color: #999;
      }

      .tv-main-panel
      {
        background-color: #222;
      }

      .chart-controls-bar
      {
        background: #222 !important;
      }

      input.symbol-edit,
      .symbol-search-dialog input {
        background-color: #222;
        border-color: #666;
        color: #aaa;
      }

      .favored-list-container span
      {
        background-color: #222;
        border-color: #666;
        color: #aaa !important;
      }
        body {background-color: black; margin: 0px;}
        span.pane-legend-line.apply-overflow-tooltip {display: none!important;}
    </style>
    <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
    <script type="text/javascript">
        var widgetLOL = new TradingView.widget({

          supports_search: false,
          supports_group_request: false,
          supports_marks: true,
          exchanges: [
            {value: "", name: "All Exchanges", desc: ""}
          ],
          symbolsTypes: [
            {name: "All types", value: ""},
            {name: "Stock", value: "stock"},
            {name: "Index", value: "index"}
          ],
          supportedResolutions: [ "1", "15"],

          fullscreen: false,
          symbol: 'BINANCE:""" + pair + """',
            autosize: true,
            timezone: "Europe/Berlin",
          interval: '""" + timeframe + """',
          allow_symbol_change: false,
          container_id: "tv_chart_container",
          //library_path: "charting_library/",
          locale: "en",
          save_image: false,
          hideideas: true,
          hide_side_toolbar: false,
          show_popup_button: false,
          withdateranges: true,
          toolbar_bg: "rgba(32,38,43,1)",
          theme: "Dark",
          studies: [
            "BB@tv-basicstudies",
            "StochasticRSI@tv-basicstudies"
          ],
        // "popup_width": "1000",
        // "popup_height": "650"
          drawings_access: { type: 'black', tools: [ { name: "Regression Trend" } ] },
          disabled_features: ["header_compare", "study_market_minimized", "control_bar", "items_favoriting" ], //"volume_force_overlay",
          enabled_features: ["seconds_resolution", "caption_buttons_text_if_possible", "narrow_chart_enabled" ],
          overrides: {
            "paneProperties.background": "#6ab9ff",
            // "paneProperties.gridProperties.color": "black",
            //
            "paneProperties.vertGridProperties.color": "#323c45",
            "paneProperties.horzGridProperties.color": "#323c45",
            "paneProperties.crossHairProperties.color": "white",
            //
            // "mainSeriesProperties.style": 0,
            // "symbolWatermarkProperties.color": "rgba(0, 0, 0, 0)",
            // "volumePaneSize": "small",
            "paneProperties.background": "red", // works
            // "mainSeriesProperties.style": 1, // candles
            // "mainSeriesProperties.priceAxisProperties.autoScale": false,
            //
            // "mainSeriesProperties.priceAxisProperties.autoScaleDisabled": "true",

            "mainSeriesProperties.candleStyle.upColor": "#94c940",
            "mainSeriesProperties.candleStyle.downColor": "#ff007a",

            // remove title etc
            "paneProperties.legendProperties.showStudyArguments": false,
            // "paneProperties.legendProperties.showStudyTitles": false,
            // "paneProperties.legendProperties.showStudyValues": false,
            // "paneProperties.legendProperties.showSeriesTitle": false,
            "paneProperties.legendProperties.showSeriesOHLC": false,

          },
          studies_overrides: {
            "bollinger bands.median.color": "blue",
            "bollinger bands.upper.color": "red",
          //   "bollinger bands.lower.color": "red",
                "BB@tv-basicstudies.upper.color": "blue",

            "bollinger bands.upper.linewidth": 14,
          //   "bollinger bands.color": "red",
          //   "bollinger bands.areaStyle.color": "red",
          //
          //   // study_Overlay@tv-basicstudies.areaStyle.color1: color
          //   // study_Overlay@tv-basicstudies.areaStyle.color2: color
          //
          //   "stochastic rsi.areaStyle.color": "red",
          //
          //   "basicstudies.areaStyle.color1": "red",
          //   "study_Overlay@tv-basicstudies.areaStyle.color2": "green",
          //   "StochasticRSI@tv-basicstudies.background.color": "green"
          },
          debug: true,
          time_frames: [
            //{ text: "50y", resolution: "6M" },
            //{ text: "1d", resolution: "5" },
          ],
          charts_storage_url: 'http://saveload.tradingview.com',
          client_id: 'tradingview.com',
          user_id: 'public_user',

          // favorites: {
          // 	intervals: ["1D", "3D", "3W", "W", "M"],
          // 	chartTypes: ["Area", "Line"]
          // },
        });
    </script>
    <!-- TradingView Widget END -->
    """
        return chart


    def build_chart_btc(pair, timeframe, exchange):
    	chart = """
		<!-- TradingView Widget BEGIN --> <style> * {
			background: black;
		}

		html,
		body {
			background: #000 none repeat scroll 0 0;
			color: #333;
			font-family: "Helvetica Neue", Helvetica, Arial, sans-serif;
		}

		a:hover {
			color: #58c3e5;
		}

		.chart-page .chart-container {
			background-color: #222;
			border-color: #444;
		}

		.header-chart-panel {
			background-color: #222;
		}

		.tv-side-toolbar {
			background-color: #222;
			border-color: #444;
			color: #999;
		}

		.tv-side-toolbar .tools-group:not(:first-child):not(.no-delimiter)::before {
			background-color: #444;
		}

		.tv-side-toolbar .tools-group .button:active:not(.subgroup),
		.tv-side-toolbar .tools-group .button.active:not(.subgroup),
		.tv-side-toolbar .tools-group .button.selected:not(.subgroup),
		.properties-toolbar .tools-group .button:active,
		.properties-toolbar .tools-group .button.active,
		.drawing-favorites-toolbar .tools-group .button:active,
		.drawing-favorites-toolbar .tools-group .button.active,
		.tv-side-toolbar .tools-group .button.selected .main,
		.tv-side-toolbar .tools-group .button:active .side,
		.tv-side-toolbar .tools-group .button.active .side {
			background-color: #444;
		}

		.tv-side-toolbar .tools-group .button .side {
			background-color: #444;
			border-color: #999;
		}

		.tv-main-panel {
			background-color: #222;
		}

		.chart-controls-bar {
			background: #222 !important;
		}

		input.symbol-edit,
		.symbol-search-dialog input {
			background-color: #222;
			border-color: #666;
			color: #aaa;
		}

		.favored-list-container span {
			background-color: #222;
			border-color: #666;
			color: #aaa !important;
		}

		body {
			background-color: black;
			margin: 0px;
		}

		span.pane-legend-line.apply-overflow-tooltip {
			display: none!important;
		}

		</style> <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script> <script type="text/javascript"> var widgetLOL=new TradingView.widget( {
			supports_search: false, supports_group_request: false, supports_marks: true, exchanges: [ {
				value: "", name: "All Exchanges", desc: ""
			}
			], symbolsTypes: [ {
				name: "All types", value: ""
			}
			, {
				name: "Stock", value: "stock"
			}
			, {
				name: "Index", value: "index"
			}
			], supportedResolutions: [ "1", "15"], fullscreen: false, symbol: '""" + exchange + """:""" + pair + """', autosize: true, timezone: "Europe/Berlin", interval: '""" + timeframe + """', toolbar_bg: '#333333', allow_symbol_change: false, container_id: "tv_chart_container", //library_path: "charting_library/",
			locale: "en", save_image: false, hideideas: true, hide_side_toolbar: false, show_popup_button: false, withdateranges: true, theme: "Dark", studies: [ "BB@tv-basicstudies", "StochasticRSI@tv-basicstudies"], // "popup_width": "1000",
			// "popup_height": "650"
			drawings_access: {
				type: 'black', tools: [ {
					name: "Regression Trend"
				}
				]
			}
			, disabled_features: ["header_compare", "study_market_minimized", "control_bar", "items_favoriting"], //"volume_force_overlay",
			enabled_features: ["seconds_resolution", "caption_buttons_text_if_possible", "narrow_chart_enabled"], overrides: {
				"paneProperties.background": "#6ab9ff", // "paneProperties.gridProperties.color": "black",
				//
				"paneProperties.vertGridProperties.color": "#323c45", "paneProperties.horzGridProperties.color": "#323c45", "paneProperties.crossHairProperties.color": "white", //
				// "mainSeriesProperties.style": 0,
				// "symbolWatermarkProperties.color": "rgba(0, 0, 0, 0)",
				// "volumePaneSize": "small",
				"paneProperties.background": "red", // works
				// "mainSeriesProperties.style": 1, // candles
				// "mainSeriesProperties.priceAxisProperties.autoScale": false,
				//
				// "mainSeriesProperties.priceAxisProperties.autoScaleDisabled": "true",
				"mainSeriesProperties.candleStyle.upColor": "#94c940", "mainSeriesProperties.candleStyle.downColor": "#ff007a", // remove title etc
				"paneProperties.legendProperties.showStudyArguments": false, // "paneProperties.legendProperties.showStudyTitles": false,
				// "paneProperties.legendProperties.showStudyValues": false,
				// "paneProperties.legendProperties.showSeriesTitle": false,
				"paneProperties.legendProperties.showSeriesOHLC": false,
			}
			, studies_overrides: {
				"bollinger bands.median.color": "blue", "bollinger bands.upper.color": "red", //   "bollinger bands.lower.color": "red",
				"BB@tv-basicstudies.upper.color": "blue", "bollinger bands.upper.linewidth": 14, //   "bollinger bands.color": "red",
				//   "bollinger bands.areaStyle.color": "red",
				//
				//   // study_Overlay@tv-basicstudies.areaStyle.color1: color
				//   // study_Overlay@tv-basicstudies.areaStyle.color2: color
				//
				//   "stochastic rsi.areaStyle.color": "red",
				//
				//   "basicstudies.areaStyle.color1": "red",
				//   "study_Overlay@tv-basicstudies.areaStyle.color2": "green",
				//   "StochasticRSI@tv-basicstudies.background.color": "green"
			}
			, debug: true, time_frames: [ //{ text: "50y", resolution: "6M" },
			//{ text: "1d", resolution: "5" },
			], charts_storage_url: 'http://saveload.tradingview.com', client_id: 'tradingview.com', user_id: 'public_user', // favorites: {
			// 	intervals: ["1D", "3D", "3W", "W", "M"],
			// 	chartTypes: ["Area", "Line"]
			// },
		}

		);
		</script> <!-- TradingView Widget END -->
    	"""
    	return chart

    @staticmethod
    def welcome_page():
        welcome_page = """
        <!DOCTYPE html>
        <html lang="en" dir="ltr">
          <head>
            <meta charset="utf-8">
            <style media="screen">
              body {
                background: #262d33;
                font-family: arial;
                font-size: 24px;
                color: #999;
              }
              a {
                color: #f3ba2e;
              }
              h1 {
                color: #f3ba2e;

              }
              #container {

                text-align: center;
              }

              #welcome {
                display: inline-block;
                margin-top: 10px;
              }
              svg{
                width: 275px;
                height: auto;
                margin-bottom: -10px;
              }

            </style>

            <title></title>
          </head>
          <body>




              <div id="container">
              <div id="welcome">
                <svg id="Logo" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="376.5" height="84.75" viewBox="0 0 502 113">
                  <metadata><?xpacket begin="﻿" id="W5M0MpCehiHzreSzNTczkc9d"?>
                <x:xmpmeta xmlns:x="adobe:ns:meta/" x:xmptk="Adobe XMP Core 5.6-c140 79.160451, 2017/05/06-01:08:21        ">
                  <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
                      <rdf:Description rdf:about=""/>
                  </rdf:RDF>
                </x:xmpmeta>

                <?xpacket end="w"?></metadata>
                <defs>
                    <style>
                      .cls-1 {
                        fill-rule: evenodd;
                      }
                    </style>
                  </defs>
                  <image id="binance" y="26" width="433" height="87" xlink:href="data:img/png;base64,iVBORw0KGgoAAAANSUhEUgAAAUUAAABBCAMAAABxTEbNAAAABGdBTUEAALGPC/xhBQAAACBjSFJNAAB6JgAAgIQAAPoAAACA6AAAdTAAAOpgAAA6mAAAF3CculE8AAAC9FBMVEXzui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui/zui8AAACc7O1SAAAA+nRSTlMAQoMGKuZ8NeKA7IEt5X427S/ngjmGLu6HMug78ITq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"/>
                  <image id="bender" x="430" width="72" height="123" xlink:href="data:img/png;base64,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"/>
                  <path class="cls-1" d="M458,68h20s-1.713,6.839-11.63,7c-9.548.115-11.37-7-11.37-7"/>
                  <image id="juri" x="74" y="13" width="299" height="32" xlink:href="data:img/png;base64,iVBORw0KGgoAAAANSUhEUgAAAOEAAAAZCAMAAADwrLk8AAAABGdBTUEAALGPC/xhBQAAACBjSFJNAAB6JgAAgIQAAPoAAACA6AAAdTAAAOpgAAA6mAAAF3CculE8AAAAaVBMVEUAAAD///8AhrgAhrgAhrgAhrgAhrgAhrgAhrgAhrgAhrgAhrgAhrgAhrgAhrgAhrgAhrgAhrgAhrgAhrgAhrgAhrgAhrgAhrgAhrgAhrgAhrgAhrgAhrgAhrgAhrgAhrgAhrgAhrgAAAD+llbGAAAAIXRSTlMAAMCQQDAgcFBggBDQ8OCgsEweeYlqLj2Y5PLVtsWnWw8DN24qAAAAAWJLR0QAiAUdSAAAAAlwSFlzAAAuIwAALiMBeKU/dgAAAAd0SU1FB+EMGxIIEnfm00YAAAOnSURBVFjD7Zdpe9sgDIAZ5rDB19r0TNfM//9PzhxC4sixrJ/2VF/sKLLQi4QAxojwIB27UW43j55vdfyF8iP7tQW5OZDbzaPnb8Jvwm/CLycUXuR/Sah0ryqlFIMxQ5M4EVphtCg/c1+pypmutFbspkYIm8eyD6uFaIwq9qHOEhJWE96dC+7fjBzdo8uq1Jopfr7N/VnCzj8mg+Et8NlsMHDbgXZaEqTgMMC2oOkwgnKNkALGcj7mn/cQdnMYhhrJxOcHs23CFM0YDQb62QQz02faISiXrWEqR6rtKKEOj4d7COP4ihjZectkbROiLAGw0PZNrUfUhdKvBTU1vEbC8Be/q0rTf2gUg1oNpwFcIPTuREoJPC0NOz1doYYpnLtYQCG0sbDcNPXq5+wfCHtqtKTMubme+SquES7obl9VfXx1C3RF7Yq2OHEOkfMF53WWTHURtSCc7+s0+4dDbzKjEMrU7zloNTXwvPcN6Bd7LDK8jb63TDEipiA2ljI3Je26I6rUe0aMDJZpTwhXMdzZS+Po1Mhg8a5GnCUckGWzsLQ0bSQSEhO6RpfGxrTwbgiMlswQcBkkDH7vI9QVocoqkOwGuWffQTn4i1Cjv3bMoDUAQrS6aKUbl6SleMsxBQOEjBCKPsz7hovhIqGoCPO2D/NaEbLMH99qMaQcqJbZwrovWgpmR5CwHOEj97Etf0Noa0Im8/3CnCdc7iJMFQt1Yq8QrkB4wEmXFaFPxVoRsgbh7tlwTOR0tUolhDxyIkNepUnrRA0L2eB1XqV4e8cVGQifUtZtRPEsGJIk2ouEPoi+mwhMSaixP2ws7zRJsk5Ti9Cwx2RpoBYF4XPKb0qAwpBmk1b4JUK7H7lXPvrC0BcIt0UNc4or2xfcOdsfqeMMzDZoddBKYzrOJ9dgLBwas92id0dy1SJkxXkr5mQqtRcJIc97NcVKaFcpEY3uVsXEisUNLZZoLSwVd54VyUFM935IVQYjqAj7Fgp4vJEwTdME3aO7QujPZ7JSu4OpqmZXk7PqCEMpxupexVs5LHaa+A/pU6QWzhKWbW22LUISuqZrLknX1C6sAePDLCfDX1lqwqwNw10Fubm9gbDYD8fyPhsHTU4hxfln0HOy21MMtdgPY/z57Ylb1iZkL69v717eXvE69XR0muMjYx9ennfdIbyCSfh18O8Ph1/vUT5PVQcMlqfo9BdeSx8Ox/jV8YBj/35saE+fbw3T00dUvn2+BM0zDBYI/wARbzFTNjd5mwAAAABJRU5ErkJggg=="/>
                </svg>
                <h1>Welcome!</h1>

                <p>To use this you have to generate an <span style="color: #f3f3f3">API Key</span>.</p>
                <p>Log into Binance and create API credentials <a href="https://www.binance.com/userCenter/createApi.html">here</a>.</p>


              </div>
            </div>

          </body>
        </html>

    """
        return welcome_page

    @staticmethod
    def build_cmc():
        """Make coin names coinmarketcap conform."""
        coin_name = val["coins"][val["pair"]]["baseAssetName"]
        if coin_name == "Wancoin":
            coin_name = "Wanchain"
        elif coin_name == "MIOTA":
            coin_name = "iota"
        elif coin_name == "Stellar Lumens":
            coin_name = "Stellar"
        elif coin_name == "EnjinCoin":
            coin_name = "enjin-coin"
        elif coin_name == "PowerLedger":
            coin_name = "power-ledger"
        elif coin_name == "BlockMason Credit Protocol":
            coin_name = "blockmason"
        elif coin_name == "Enigma":
            coin_name = "enigma-project"
        elif coin_name == "KyberNetwork":
            coin_name = "kyber-network"
        elif coin_name == "NeoGas":
            coin_name = "gas"
        elif coin_name == "Agrello":
            coin_name = "agrello-delta"
        elif coin_name == "Ambrosus":
            coin_name = "amber"
        elif coin_name == "iExecRLC":
            coin_name = "rlc"
        print("Generating CMC url: " + str(coin_name))
        url = "https://coinmarketcap.com/currencies/" + coin_name.replace(" ", "-").replace(".", "") + "/"
        return url

    @staticmethod
    def build_binance_info():
        coin_name = val["coins"][val["pair"]]["baseAssetName"]
        url = "https://info.binance.com/currencies/" + coin_name.replace(" ", "-").replace(".", "") + "/"
        return url